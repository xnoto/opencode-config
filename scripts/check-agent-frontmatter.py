#!/usr/bin/env python3
"""Validate OpenCode agent definitions and config agent references.

Checks every agents/*.md frontmatter against the documented OpenCode agent
field set, and cross-checks agent references in opencode.jsonc (or legacy
opencode.json) against the agents actually defined.

Runs from the repository root; intended for pre-commit and CI.
"""

import json
import sys
from pathlib import Path

import json5
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "model",
    "variant",
    "description",
    "mode",
    "hidden",
    "color",
    "steps",
    "options",
    "permission",
    "permissions",
    "disable",
    "temperature",
    "top_p",
}

# Per the OpenCode agents docs, extra frontmatter fields are passed through to
# the provider as model options. These provider-level reasoning controls are
# used deliberately in this repo, so they are allowlisted; any other unknown
# field is treated as a likely typo of a documented field and fails the check.
ALLOWED_PROVIDER_OPTION_KEYS = {
    "reasoningEffort",
    "reasoningMode",
}

VALID_MODES = {"primary", "subagent", "all"}
VALID_PERMISSION_ACTIONS = {"allow", "ask", "deny"}

# Built-in agents that can serve as primaries unless disabled in config.
BUILTIN_PRIMARY_AGENTS = {"build", "plan"}

errors = []


def fail(location, message):
    errors.append(f"{location}: {message}")


def parse_frontmatter(path):
    """Return (frontmatter dict, error string or None)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing opening --- frontmatter delimiter"
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            try:
                data = yaml.safe_load("\n".join(lines[1:i]))
            except yaml.YAMLError as exc:
                return None, f"frontmatter is not valid YAML: {exc}"
            if not isinstance(data, dict):
                return None, "frontmatter must be a YAML mapping"
            return data, None
    return None, "missing closing --- frontmatter delimiter"


def check_permission(location, permission):
    if isinstance(permission, str):
        if permission not in VALID_PERMISSION_ACTIONS:
            fail(location, f"permission action must be one of {sorted(VALID_PERMISSION_ACTIONS)}, got {permission!r}")
        return
    if not isinstance(permission, dict):
        fail(location, "permission must be a string action or a mapping of tool rules")
        return
    for tool, rule in permission.items():
        if isinstance(rule, str):
            if rule not in VALID_PERMISSION_ACTIONS:
                fail(location, f"permission.{tool} must be one of {sorted(VALID_PERMISSION_ACTIONS)}, got {rule!r}")
        elif isinstance(rule, dict):
            for pattern, action in rule.items():
                if action not in VALID_PERMISSION_ACTIONS:
                    fail(
                        location,
                        f"permission.{tool}[{pattern!r}] must be one of {sorted(VALID_PERMISSION_ACTIONS)}, got {action!r}",
                    )
        else:
            fail(location, f"permission.{tool} must be a string action or a pattern mapping")


def check_permissions(location, permissions):
    if not isinstance(permissions, list):
        fail(location, "permissions must be a list of rule mappings")
        return
    fields = {"action", "resource", "effect"}
    for index, rule in enumerate(permissions):
        label = f"permissions[{index}]"
        if not isinstance(rule, dict):
            fail(location, f"{label} must be a mapping")
            continue
        unknown = sorted(set(rule) - fields, key=str)
        missing = sorted(fields - set(rule))
        if unknown:
            fail(location, f"{label} has unknown rule fields {unknown}")
        if missing:
            fail(location, f"{label} is missing rule fields {missing}")
        for key in fields:
            if key in rule and (not isinstance(rule[key], str) or not rule[key].strip()):
                fail(location, f"{label}.{key} must be a nonempty string")
        effect = rule.get("effect")
        if isinstance(effect, str) and effect not in VALID_PERMISSION_ACTIONS:
            fail(location, f"{label}.effect must be allow, ask, or deny")


def check_agent_file(path):
    location = path.relative_to(REPO_ROOT)
    frontmatter, error = parse_frontmatter(path)
    if error:
        fail(location, error)
        return None

    unknown = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_KEYS - ALLOWED_PROVIDER_OPTION_KEYS)
    if unknown:
        fail(
            location,
            f"unknown frontmatter field(s) {unknown}; OpenCode passes unknown fields through to the provider as "
            f"model options - if deliberate, add them to ALLOWED_PROVIDER_OPTION_KEYS in this script, "
            f"otherwise fix the typo",
        )

    if "description" not in frontmatter or not str(frontmatter.get("description", "")).strip():
        fail(location, "missing description; agents without one cannot be selected or delegated to reliably")

    mode = frontmatter.get("mode")
    if mode is not None and mode not in VALID_MODES:
        fail(location, f"mode must be one of {sorted(VALID_MODES)}, got {mode!r}")

    steps = frontmatter.get("steps")
    if steps is not None and (not isinstance(steps, int) or isinstance(steps, bool) or steps < 1):
        fail(location, f"steps must be a positive integer, got {steps!r}")

    if "permission" in frontmatter and "permissions" in frontmatter:
        fail(location, "both legacy permission and native permissions are set; use one format per agent")
    if "permission" in frontmatter:
        check_permission(location, frontmatter["permission"])
    if "permissions" in frontmatter:
        check_permissions(location, frontmatter["permissions"])

    return {
        "name": frontmatter.get("name", path.stem),
        # Per the OpenCode docs, mode defaults to "all" when unspecified.
        "mode": mode or "all",
        "hidden": bool(frontmatter.get("hidden", False)),
        "disabled": bool(frontmatter.get("disable", False)),
    }


def load_config(path):
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".jsonc":
            data = json5.loads(text, allow_duplicate_keys=False)
        else:
            data = json.loads(text)
    except ValueError:
        fail(path.name, "must contain valid UTF-8 JSON/JSONC")
        return {}
    except OSError:
        fail(path.name, "could not read config")
        return {}
    if not isinstance(data, dict):
        fail(path.name, "config must be an object")
        return {}
    return data


def check_config(agents):
    # The repository's canonical config is JSONC. Fall back to JSON for older checkouts.
    path = REPO_ROOT / "opencode.jsonc"
    if not path.exists() and not path.is_symlink():
        path = REPO_ROOT / "opencode.json"
    if not path.exists() and not path.is_symlink():
        fail("opencode.jsonc", "missing config (expected opencode.jsonc or opencode.json)")
        return
    location = path.name
    config = load_config(path)

    inline_agents = config.get("agent", {})
    if not isinstance(inline_agents, dict):
        fail(location, "agent must be an object keyed by agent name")
        inline_agents = {}
    for name, block in inline_agents.items():
        if not isinstance(block, dict):
            fail(location, f"agent {name!r} must be an object")

    if "default_agent" not in config:
        return
    default_agent = config["default_agent"]
    if not isinstance(default_agent, str) or not default_agent.strip():
        fail(location, "default_agent must be a nonempty string")
        return

    block = inline_agents.get(default_agent, {})
    if not isinstance(block, dict):
        return  # Already reported above.
    target = agents.get(default_agent)
    if target is None and default_agent not in BUILTIN_PRIMARY_AGENTS and default_agent not in inline_agents:
        fail(location, f"default_agent {default_agent!r} does not match any defined agent")
        return
    if target is None:
        target = {
            "mode": block.get("mode", "primary"),
            "hidden": block.get("hidden"),
            "disabled": block.get("disable"),
        }
    mode = target["mode"]
    if mode not in ("primary", "all"):
        fail(location, f"default_agent {default_agent!r} must be a primary-mode agent, got mode {mode!r}")
    if target["hidden"]:
        fail(location, f"default_agent {default_agent!r} must not be hidden")
    if target["disabled"]:
        fail(location, f"default_agent {default_agent!r} is disabled")


def main():
    errors.clear()
    agent_files = sorted(AGENTS_DIR.glob("*.md"))
    if not agent_files:
        fail("agents/", "no agent definition files found")

    agents = {}
    for path in agent_files:
        info = check_agent_file(path)
        if info:
            if info["name"] in agents:
                fail(path.relative_to(REPO_ROOT), f"duplicate agent name {info['name']!r}")
            agents[info["name"]] = info

    check_config(agents)

    if errors:
        print("Agent definition validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(f"Agent definition validation passed ({len(agent_files)} agent files checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate OpenCode agent definitions and config agent references.

Checks every agents/*.md frontmatter against the documented OpenCode agent
field set, and cross-checks opencode.json agent-related keys (default_agent,
inline agent blocks, disabled built-ins) against the agents actually defined.

Runs from the repository root; intended for pre-commit and CI.
"""

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"
CONFIG_FILE = REPO_ROOT / "opencode.json"

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

    if "permission" in frontmatter:
        check_permission(location, frontmatter["permission"])

    return {
        "name": frontmatter.get("name", path.stem),
        # Per the OpenCode docs, mode defaults to "all" when unspecified.
        "mode": mode or "all",
        "hidden": bool(frontmatter.get("hidden", False)),
        "disabled": bool(frontmatter.get("disable", False)),
    }


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail("opencode.json", f"invalid JSON: {exc}")
        return {}


def main():
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

    config = load_config()
    inline_agents = config.get("agent", {})
    if not isinstance(inline_agents, dict):
        fail("opencode.json", "agent must be an object keyed by agent name")
        inline_agents = {}

    disabled_builtins = {name for name, block in inline_agents.items() if isinstance(block, dict) and block.get("disable")}

    default_agent = config.get("default_agent")
    if default_agent:
        target = agents.get(default_agent)
        if target:
            if target["mode"] not in ("primary", "all"):
                fail("opencode.json", f"default_agent {default_agent!r} must be a primary-mode agent, got mode {target['mode']!r}")
            if target["hidden"]:
                fail("opencode.json", f"default_agent {default_agent!r} must not be hidden")
            if target["disabled"]:
                fail("opencode.json", f"default_agent {default_agent!r} is disabled")
        elif default_agent in BUILTIN_PRIMARY_AGENTS and default_agent not in disabled_builtins:
            pass
        elif default_agent in inline_agents and not default_agent in disabled_builtins:
            block = inline_agents[default_agent]
            mode = block.get("mode", "primary") if isinstance(block, dict) else "primary"
            if mode not in ("primary", "all"):
                fail("opencode.json", f"default_agent {default_agent!r} must be a primary-mode agent, got mode {mode!r}")
            if isinstance(block, dict) and block.get("hidden"):
                fail("opencode.json", f"default_agent {default_agent!r} must not be hidden")
        else:
            fail("opencode.json", f"default_agent {default_agent!r} does not match any defined agent")

    if errors:
        print("Agent definition validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(f"Agent definition validation passed ({len(agent_files)} agent files checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

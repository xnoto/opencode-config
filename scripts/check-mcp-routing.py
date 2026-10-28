#!/usr/bin/env python3
"""Check source-level MCP search availability and fallback permission guards."""

import re
import sys
from pathlib import Path

import json5

REPO_ROOT = Path(__file__).resolve().parent.parent
SEARCH_ACTIONS = ("parallel-search_web_search", "parallel-search_web_fetch")
FALLBACK_ACTIONS = ("websearch", "webfetch")


def effective_permission(permissions, action):
    result = None
    for pattern, rule in permissions.items():
        expression = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")
        if re.fullmatch(expression, action):
            result = rule
    return result


def validate_config(config):
    if not isinstance(config, dict):
        return ["OpenCode config must contain an object"]

    errors = []
    servers = config.get("mcp")
    server = servers.get("parallel-search") if isinstance(servers, dict) else None
    if not isinstance(server, dict) or server.get("enabled") is not True:
        errors.append("parallel-search must be enabled in the repository's legacy MCP map")

    permissions = config.get("permission")
    if not isinstance(permissions, dict):
        return errors + ["expected the repository's legacy permission map; review guards on migration"]
    for action in SEARCH_ACTIONS:
        if effective_permission(permissions, action) != "allow":
            errors.append(f"{action} must be allowed")
    for action in FALLBACK_ACTIONS:
        rule = effective_permission(permissions, action)
        if not isinstance(rule, str) or rule not in {"ask", "deny"}:
            errors.append(f"{action} must require approval or be denied")
    return errors


def validate_repository(repo_root):
    try:
        config = json5.loads(
            (repo_root / "opencode.jsonc").read_text(encoding="utf-8"),
            allow_duplicate_keys=False,
        )
    except (ValueError, UnicodeError, OSError):
        return ["could not read valid, unambiguous opencode.jsonc"]
    return validate_config(config)


def main(repo_root=REPO_ROOT):
    errors = validate_repository(repo_root)
    if errors:
        print("MCP routing validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("MCP routing source guards passed (not an effective-runtime or behavioral check).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

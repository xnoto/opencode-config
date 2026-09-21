#!/usr/bin/env python3
"""Validate the repository-owned opencode-mem safe-default contract."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "opencode-mem.json"

EXPECTED = {
    "storagePath": "~/.opencode-mem/data",
    "embeddingModel": "Xenova/nomic-embed-text-v1",
    "autoCaptureEnabled": False,
    "injectProfile": False,
    "webServerEnabled": False,
}


def is_disabled_block(value):
    return (
        isinstance(value, dict)
        and set(value) == {"enabled"}
        and type(value["enabled"]) is bool
        and value["enabled"] is False
    )


def main():
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"missing {CONFIG_FILE.name}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid {CONFIG_FILE.name}: {exc}", file=sys.stderr)
        return 1

    errors = []
    for key, expected in EXPECTED.items():
        actual = config.get(key)
        if type(expected) is bool:
            valid = type(actual) is bool and actual is expected
        else:
            valid = actual == expected
        if not valid:
            errors.append(f"{key} must be {expected!r}, got {actual!r}")

    if config.get("memory") != {"defaultScope": "project"}:
        errors.append("memory must be {'defaultScope': 'project'}")
    for key in ("chatMessage", "compaction"):
        if not is_disabled_block(config.get(key)):
            errors.append(f"{key} must be {{'enabled': False}}")

    if errors:
        print("opencode-mem safe-default validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print("opencode-mem safe-default validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

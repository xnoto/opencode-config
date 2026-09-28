#!/usr/bin/env python3
"""Validate the repository-owned opencode-mem safe-default contract."""

import json
import stat
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_NAME = "opencode-mem.json"
FORBIDDEN_CONFIG_PATHS = (
    "opencode-mem.jsonc",
    ".opencode/opencode-mem.json",
    ".opencode/opencode-mem.jsonc",
)

EXPECTED = {
    "storagePath": "~/.opencode-mem/data",
    "embeddingModel": "Xenova/nomic-embed-text-v1",
    "autoCaptureEnabled": False,
    "injectProfile": False,
    "webServerEnabled": False,
}
ALLOWED_KEYS = set(EXPECTED) | {"memory", "chatMessage", "compaction"}


def is_disabled_block(value):
    return (
        isinstance(value, dict)
        and set(value) == {"enabled"}
        and type(value["enabled"]) is bool
        and value["enabled"] is False
    )


def validate_config(config):
    if not isinstance(config, dict):
        return [f"{CONFIG_NAME} must contain a JSON object"]

    errors = []
    if set(config) - ALLOWED_KEYS:
        errors.append(f"{CONFIG_NAME} contains unapproved top-level settings")
    for key, expected in EXPECTED.items():
        actual = config.get(key)
        if type(expected) is bool:
            valid = type(actual) is bool and actual is expected
        else:
            valid = actual == expected
        if not valid:
            errors.append(f"{key} must be {expected!r}")

    if config.get("memory") != {"defaultScope": "project"}:
        errors.append("memory must be {'defaultScope': 'project'}")
    for key in ("chatMessage", "compaction"):
        if not is_disabled_block(config.get(key)):
            errors.append(f"{key} must be {{'enabled': False}}")
    return errors


def validate_repository(repo_root):
    errors = []
    for relative_path in FORBIDDEN_CONFIG_PATHS:
        path = repo_root / relative_path
        if path.exists() or path.is_symlink():
            errors.append(f"{relative_path} is not allowed to shadow or override {CONFIG_NAME}")

    config_file = repo_root / CONFIG_NAME
    try:
        if not stat.S_ISREG(config_file.lstat().st_mode):
            errors.append(f"{CONFIG_NAME} must be a regular file, not a symlink or special file")
            return errors
        config = json.loads(config_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing {CONFIG_NAME}")
    except (json.JSONDecodeError, UnicodeError):
        errors.append(f"{CONFIG_NAME} must contain valid UTF-8 JSON")
    except OSError:
        errors.append(f"could not read {CONFIG_NAME}")
    else:
        errors.extend(validate_config(config))
    return errors


def main(repo_root=REPO_ROOT):
    errors = validate_repository(repo_root)

    if errors:
        print("opencode-mem safe-default validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print("opencode-mem safe-default validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate the repository-owned opencode-mem safe-default contract."""

import json
import stat
import sys
from pathlib import Path

import json5

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_NAMES = ("opencode-mem.json", "opencode-mem.jsonc")
FORBIDDEN_CONFIG_PATHS = (
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


def validate_config(config, config_name="opencode-mem config"):
    if not isinstance(config, dict):
        return [f"{config_name} must contain a JSON object"]

    errors = []
    if set(config) - ALLOWED_KEYS:
        errors.append(f"{config_name} contains unapproved top-level settings")
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
            errors.append(f"{relative_path} is not allowed to shadow or override opencode-mem config")
    if errors:
        return errors

    candidates = [repo_root / name for name in CONFIG_NAMES]
    present = [path for path in candidates if path.exists() or path.is_symlink()]
    if len(present) > 1:
        return errors + ["multiple opencode-mem config files are not allowed"]
    if not present:
        return errors + ["missing opencode-mem config (expected opencode-mem.json or opencode-mem.jsonc)"]

    config_file = present[0]
    config_name = config_file.name
    try:
        if not stat.S_ISREG(config_file.lstat().st_mode):
            errors.append(f"{config_name} must be a regular file, not a symlink or special file")
            return errors
        text = config_file.read_text(encoding="utf-8")
        if config_file.suffix == ".jsonc":
            config = json5.loads(text, allow_duplicate_keys=False)
        else:
            config = json.loads(text)
    except (json.JSONDecodeError, ValueError, UnicodeError):
        errors.append(f"{config_name} must contain valid UTF-8 JSON/JSONC")
    except OSError:
        errors.append(f"could not read {config_name}")
    else:
        errors.extend(validate_config(config, config_name))
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

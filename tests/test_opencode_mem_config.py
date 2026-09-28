import contextlib
import copy
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "check_opencode_mem_config", REPO_ROOT / "scripts/check-opencode-mem-config.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

VALID_CONFIG = {
    "storagePath": "~/.opencode-mem/data",
    "embeddingModel": "Xenova/nomic-embed-text-v1",
    "memory": {"defaultScope": "project"},
    "autoCaptureEnabled": False,
    "injectProfile": False,
    "webServerEnabled": False,
    "chatMessage": {"enabled": False},
    "compaction": {"enabled": False},
}


class MemoryConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.config_file = self.root / "opencode-mem.json"
        self.config_file.write_text(json.dumps(VALID_CONFIG), encoding="utf-8")

    def test_current_config_is_valid(self):
        self.assertEqual(validator.validate_config(VALID_CONFIG), [])
        self.assertEqual(validator.validate_repository(self.root), [])

    def test_non_object_roots_are_rejected(self):
        for value in (None, [], "config", 0, False):
            with self.subTest(value=value):
                self.assertEqual(
                    validator.validate_config(value),
                    ["opencode-mem.json must contain a JSON object"],
                )

    def test_every_required_setting_is_required(self):
        for key in VALID_CONFIG:
            with self.subTest(key=key):
                config = copy.deepcopy(VALID_CONFIG)
                del config[key]
                self.assertTrue(validator.validate_config(config))

    def test_unapproved_settings_are_rejected(self):
        for key in ("embeddingApiUrl", "embeddingApiKey", "memoryProvider", "unknown"):
            with self.subTest(key=key):
                config = {**VALID_CONFIG, key: "sensitive-placeholder"}
                self.assertEqual(
                    validator.validate_config(config),
                    ["opencode-mem.json contains unapproved top-level settings"],
                )

    def test_fixed_storage_and_model_are_enforced(self):
        for key in ("storagePath", "embeddingModel"):
            with self.subTest(key=key):
                config = {**VALID_CONFIG, key: "different"}
                self.assertTrue(validator.validate_config(config))

    def test_top_level_automation_must_be_boolean_false(self):
        for key in ("autoCaptureEnabled", "injectProfile", "webServerEnabled"):
            for value in (True, 0, "false", None):
                with self.subTest(key=key, value=value):
                    self.assertTrue(validator.validate_config({**VALID_CONFIG, key: value}))

    def test_nested_automation_must_be_exactly_disabled(self):
        for key in ("chatMessage", "compaction"):
            for value in (
                {"enabled": True},
                {"enabled": 0},
                {"enabled": "false"},
                {"enabled": False, "extra": False},
                {},
                None,
            ):
                with self.subTest(key=key, value=value):
                    self.assertTrue(validator.validate_config({**VALID_CONFIG, key: value}))

    def test_project_scope_is_exact(self):
        for value in (
            {"defaultScope": "all-projects"},
            {"defaultScope": "user"},
            {"defaultScope": "project", "extra": True},
            {},
            None,
        ):
            with self.subTest(value=value):
                self.assertTrue(validator.validate_config({**VALID_CONFIG, "memory": value}))

    def test_shadow_and_override_files_are_rejected_without_reading(self):
        for relative_path in validator.FORBIDDEN_CONFIG_PATHS:
            with self.subTest(path=relative_path):
                path = self.root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("invalid sensitive-placeholder", encoding="utf-8")
                errors = validator.validate_repository(self.root)
                self.assertEqual(len(errors), 1)
                self.assertIn(relative_path, errors[0])
                self.assertNotIn("sensitive-placeholder", errors[0])
                path.unlink()

    def test_dangling_shadow_symlinks_are_rejected(self):
        for relative_path in validator.FORBIDDEN_CONFIG_PATHS:
            with self.subTest(path=relative_path):
                path = self.root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(self.root / "missing")
                self.assertTrue(validator.validate_repository(self.root))
                path.unlink()

    def test_missing_config_is_rejected(self):
        self.config_file.unlink()
        self.assertEqual(
            validator.validate_repository(self.root), ["missing opencode-mem.json"]
        )

    def test_invalid_json_and_encoding_are_rejected(self):
        for content in (b"{", b"\xff"):
            with self.subTest(content=content):
                self.config_file.write_bytes(content)
                self.assertEqual(
                    validator.validate_repository(self.root),
                    ["opencode-mem.json must contain valid UTF-8 JSON"],
                )

    def test_config_directory_is_rejected(self):
        self.config_file.unlink()
        self.config_file.mkdir()
        self.assertIn("must be a regular file", validator.validate_repository(self.root)[0])

    def test_config_symlink_is_rejected_without_reading_target(self):
        self.config_file.unlink()
        self.config_file.symlink_to(self.root / "missing")
        self.assertIn("must be a regular file", validator.validate_repository(self.root)[0])
        (self.root / "missing").write_text("sensitive-placeholder", encoding="utf-8")
        self.assertIn("must be a regular file", validator.validate_repository(self.root)[0])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires FIFO support")
    def test_config_fifo_is_rejected_without_opening(self):
        self.config_file.unlink()
        os.mkfifo(self.config_file)
        self.assertIn("must be a regular file", validator.validate_repository(self.root)[0])

    def test_unreadable_config_is_rejected(self):
        with mock.patch.object(Path, "read_text", side_effect=PermissionError):
            errors = validator.validate_repository(self.root)
        self.assertEqual(
            errors, ["could not read opencode-mem.json"]
        )

    def test_main_reports_success(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = validator.main(self.root)
        self.assertEqual(status, 0)
        self.assertIn("validation passed", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_main_fails_without_echoing_untrusted_values(self):
        config = {**VALID_CONFIG, "storagePath": "sensitive-placeholder"}
        self.config_file.write_text(json.dumps(config), encoding="utf-8")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = validator.main(self.root)
        self.assertEqual(status, 1)
        self.assertIn("validation failed", stderr.getvalue())
        self.assertNotIn("sensitive-placeholder", stdout.getvalue() + stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

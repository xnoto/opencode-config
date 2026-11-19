import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "check_agent_frontmatter", ROOT / "scripts/check-agent-frontmatter.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

ROLES = (
    "adversarial-code-reviewer", "qa-engineer", "docs-writer",
    "infra-security-reviewer", "devops-engineer", "release-engineer",
    "cloud-architecture-reviewer",
)
DENY_ALL = [{"action": "*", "resource": "*", "effect": "deny"}]


class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patcher = mock.patch.object(validator, "REPO_ROOT", self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.addCleanup(validator.errors.clear)

    def check(self, **fields):
        validator.errors.clear()
        data = {"description": "Test reviewer", "mode": "subagent", **fields}
        path = self.root / "agent.md"
        path.write_text("---\n" + yaml.safe_dump(data) + "---\n\nReview.\n", encoding="utf-8")
        validator.check_agent_file(path)
        return list(validator.errors)

    def test_native_deny_all(self):
        self.assertEqual(self.check(permissions=DENY_ALL), [])

    def test_ordered_native_rules(self):
        rules = DENY_ALL + [{"action": "read", "resource": "src/**", "effect": "allow"}]
        self.assertEqual(self.check(permissions=rules), [])

    def test_empty_native_rules_are_valid_shape_not_isolation(self):
        self.assertEqual(self.check(permissions=[]), [])

    def test_legacy_permissions_preserved(self):
        for value in ("deny", {"edit": "deny", "bash": {"*": "deny"}}):
            with self.subTest(value=value):
                self.assertEqual(self.check(permission=value), [])

    def test_invalid_legacy_action(self):
        self.assertTrue(self.check(permission="maybe"))

    def test_native_requires_list(self):
        for value in ({"action": "*"}, "deny", 42, None):
            with self.subTest(value=value):
                errors = self.check(permissions=value)
                self.assertTrue(any("must be a list" in error for error in errors), errors)

    def test_native_rule_requires_mapping(self):
        for value in ("deny", 42, None, []):
            with self.subTest(value=value):
                errors = self.check(permissions=[value])
                self.assertTrue(any("must be a mapping" in error for error in errors), errors)

    def test_native_rule_fields(self):
        for field in ("action", "resource", "effect"):
            for value in ("", " ", None, 42, True, []):
                with self.subTest(field=field, value=value):
                    rule = {**DENY_ALL[0], field: value}
                    errors = self.check(permissions=[rule])
                    self.assertTrue(any("nonempty string" in error for error in errors), errors)

    def test_missing_field(self):
        for field in ("action", "resource", "effect"):
            with self.subTest(field=field):
                rule = dict(DENY_ALL[0])
                del rule[field]
                errors = self.check(permissions=[rule])
                self.assertTrue(any("missing rule fields" in error for error in errors), errors)

    def test_unknown_field(self):
        for field in ("scope", 42):
            with self.subTest(field=field):
                errors = self.check(permissions=[{**DENY_ALL[0], field: "repo"}])
                self.assertTrue(any("unknown rule fields" in error for error in errors), errors)

    def test_bad_effect(self):
        errors = self.check(permissions=[{**DENY_ALL[0], "effect": "maybe"}])
        self.assertTrue(any("must be allow, ask, or deny" in error for error in errors), errors)

    def test_both_formats_rejected(self):
        errors = self.check(permission="deny", permissions=DENY_ALL)
        self.assertTrue(any("use one format" in error for error in errors), errors)


class AgentConfigTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.agents = self.root / "agents"
        self.agents.mkdir()
        for name, fields in {
            "primary": {"mode": "primary"},
            "reviewer": {"mode": "subagent"},
            "hidden": {"mode": "primary", "hidden": True},
            "disabled": {"mode": "primary", "disable": True},
        }.items():
            data = {"description": "Test agent", **fields}
            (self.agents / f"{name}.md").write_text(
                "---\n" + yaml.safe_dump(data) + "---\n", encoding="utf-8"
            )
        self.addCleanup(validator.errors.clear)

    def run_validator(self):
        stderr = io.StringIO()
        with mock.patch.multiple(validator, REPO_ROOT=self.root, AGENTS_DIR=self.agents):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                status = validator.main()
        return status, stderr.getvalue()

    def test_jsonc_is_checked_even_with_valid_legacy_json(self):
        (self.root / "opencode.json").write_text('{"default_agent":"primary"}', encoding="utf-8")
        path = self.root / "opencode.jsonc"
        path.write_text('// tracked config\n{"default_agent":"missing",}\n', encoding="utf-8")
        status, stderr = self.run_validator()
        self.assertEqual(status, 1)
        self.assertIn("opencode.jsonc: default_agent 'missing' does not match", stderr)
        path.write_text('// tracked config\n{"default_agent":"primary",}\n', encoding="utf-8")
        self.assertEqual(self.run_validator(), (0, ""))

    def test_legacy_json_is_checked_and_keeps_strict_syntax(self):
        path = self.root / "opencode.json"
        for text, expected in (
            ('{"default_agent":"primary"}', None),
            ('{"default_agent":"missing"}', "default_agent 'missing' does not match"),
            ('{"default_agent":"primary",}', "must contain valid UTF-8 JSON/JSONC"),
        ):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                status, stderr = self.run_validator()
                self.assertEqual(status, int(expected is not None))
                if expected is not None:
                    self.assertIn(f"opencode.json: {expected}", stderr)

    def test_default_agent_must_be_selectable(self):
        path = self.root / "opencode.jsonc"
        for default, inline, expected in (
            ("reviewer", {}, "must be a primary-mode agent"),
            ("hidden", {}, "must not be hidden"),
            ("disabled", {}, "is disabled"),
            ("plan", {"plan": {"disable": True}}, "is disabled"),
            ("inline", {"inline": {"mode": "subagent"}}, "must be a primary-mode agent"),
            ("inline", {"inline": False}, "must be an object"),
            ("build", {}, None),
            ("inline", {"inline": {"mode": "primary"}}, None),
        ):
            with self.subTest(default=default, inline=inline):
                path.write_text(json.dumps({"default_agent": default, "agent": inline}), encoding="utf-8")
                status, stderr = self.run_validator()
                self.assertEqual(status, int(expected is not None))
                if expected is not None:
                    self.assertIn(expected, stderr)

    def test_missing_and_malformed_configs_fail_cleanly(self):
        path = self.root / "opencode.jsonc"
        for text, expected in (
            (None, "missing config"),
            (b"{", "must contain valid UTF-8 JSON/JSONC"),
            (b"\xff", "must contain valid UTF-8 JSON/JSONC"),
            (b'{"agent": {}, "agent": {}}', "must contain valid UTF-8 JSON/JSONC"),
            (b"[]", "config must be an object"),
            (b'{"agent": []}', "agent must be an object"),
            (b'{"default_agent": []}', "default_agent must be a nonempty string"),
        ):
            with self.subTest(text=text):
                if text is not None:
                    path.write_bytes(text)
                status, stderr = self.run_validator()
                self.assertEqual(status, 1)
                self.assertIn(f"opencode.jsonc: {expected}", stderr)


class SpecialistRosterTests(unittest.TestCase):
    def test_seven_supplied_material_roles(self):
        for name in ROLES:
            with self.subTest(name=name):
                data, error = validator.parse_frontmatter(ROOT / "agents" / f"{name}.md")
                self.assertIsNone(error)
                self.assertEqual(data["mode"], "subagent")
                self.assertEqual(data["permissions"], DENY_ALL)
                self.assertEqual(set(data), {"description", "mode", "permissions"})

    def test_old_reviewer_removed(self):
        self.assertFalse((ROOT / "agents/bullshit-detector.md").exists())
        for path in (ROOT / "agents").glob("*.md"):
            with self.subTest(agent=path.name):
                self.assertNotIn("bullshit-detector", path.read_text(encoding="utf-8"))

    def test_claude_agent_removed(self):
        self.assertFalse((ROOT / "agents/claude.md").exists())


if __name__ == "__main__":
    unittest.main()

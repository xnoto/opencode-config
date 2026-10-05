import importlib.util
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
        self.assertNotIn("bullshit-detector", (ROOT / "agents/claude.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

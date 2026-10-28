import contextlib
import copy
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "check_mcp_routing", REPO_ROOT / "scripts/check-mcp-routing.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

VALID_CONFIG = {
    "mcp": {"parallel-search": {"enabled": True}},
    "permission": {
        "*": "ask",
        "parallel-search_*": "allow",
        "websearch": "ask",
        "webfetch": "ask",
    },
}


class RoutingConfigTests(unittest.TestCase):
    def test_current_repository(self):
        self.assertEqual(validator.validate_repository(REPO_ROOT), [])

    def test_valid_guards(self):
        self.assertEqual(validator.validate_config(VALID_CONFIG), [])

    def test_invalid_roots(self):
        for value in (None, [], False, "config"):
            with self.subTest(value=value):
                self.assertTrue(validator.validate_config(value))

    def test_parallel_search_must_be_enabled(self):
        for value in (None, {}, {"enabled": False}, {"enabled": 1}):
            with self.subTest(value=value):
                config = copy.deepcopy(VALID_CONFIG)
                config["mcp"]["parallel-search"] = value
                self.assertTrue(validator.validate_config(config))

    def test_missing_or_migrated_mcp_shape_requires_review(self):
        for value in (None, [], {"servers": VALID_CONFIG["mcp"]}):
            with self.subTest(value=value):
                self.assertTrue(validator.validate_config({**VALID_CONFIG, "mcp": value}))

    def test_both_search_actions_must_be_allowed(self):
        for action in validator.SEARCH_ACTIONS:
            for rule in ("ask", "deny", None, {"*": "allow"}):
                with self.subTest(action=action, rule=rule):
                    config = copy.deepcopy(VALID_CONFIG)
                    config["permission"][action] = rule
                    self.assertTrue(validator.validate_config(config))

    def test_builtin_fallbacks_cannot_be_silently_allowed(self):
        for action in validator.FALLBACK_ACTIONS:
            for rule in ("allow", None, True, {"*": "allow"}):
                with self.subTest(action=action, rule=rule):
                    config = copy.deepcopy(VALID_CONFIG)
                    config["permission"][action] = rule
                    self.assertTrue(validator.validate_config(config))

    def test_strict_denies_are_accepted(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["permission"].update(websearch="deny", webfetch="deny")
        self.assertEqual(validator.validate_config(config), [])

    def test_last_matching_wildcard_controls_the_permission(self):
        config = copy.deepcopy(VALID_CONFIG)
        config["permission"]["web*"] = "allow"
        self.assertTrue(validator.validate_config(config))
        config["permission"]["*"] = config["permission"].pop("*")
        self.assertTrue(validator.validate_config(config))
        self.assertEqual(
            validator.effective_permission({"*": "allow", "web*": "ask"}, "websearch"),
            "ask",
        )

    def test_only_star_and_question_mark_are_wildcards(self):
        self.assertEqual(
            validator.effective_permission({"*": "ask", "web[fs]*": "allow"}, "websearch"),
            "ask",
        )
        self.assertEqual(
            validator.effective_permission({"*": "ask", "websearc?": "deny"}, "websearch"),
            "deny",
        )
        self.assertIsNone(validator.effective_permission({"web": "allow"}, "websearch"))

    def test_missing_permission_map_requires_review(self):
        for value in (None, [], "allow"):
            with self.subTest(value=value):
                self.assertTrue(validator.validate_config({**VALID_CONFIG, "permission": value}))

    def test_repository_read_errors_do_not_echo_config_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for text in (None, '{"private-placeholder":', '{"permission": {}, "permission": {}}'):
                if text is not None:
                    (root / "opencode.jsonc").write_text(text, encoding="utf-8")
                stdout, stderr = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    self.assertEqual(validator.main(root), 1)
                self.assertNotIn("private-placeholder", stdout.getvalue() + stderr.getvalue())


class RoutingInstructionTests(unittest.TestCase):
    def test_source_selection_table_retains_dedicated_routes(self):
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        table = text.split("## Source selection (all tool-capable agents)", 1)[1]
        table = table.split("## Required skill loading", 1)[0]
        for task, route in (
            ("General public-web discovery", "`parallel-search` `web_search`"),
            ("Library/framework documentation", "`context7`"),
            ("AWS / Terraform / OpenTofu documentation", "`aws-docs` / `terraform-docs` / `opentofu-docs`"),
            ("OpenCode behavior or configuration", "official V2 docs"),
            ("Remote GitHub repository content", "`github`"),
            ("Internal decisions", "`notion`"),
            ("Substantial analysis", "`context-mode`"),
            ("Focused excerpts", "`parallel-search` `web_fetch`"),
            ("Live cloud", "clarify an unspecified target"),
        ):
            with self.subTest(task=task):
                row = next(line for line in table.splitlines() if line.startswith(f"| {task}"))
                self.assertIn(route, row)
        self.assertIn("request explicit approval", table)

    def test_search_is_not_described_as_last_resort(self):
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        section = text.split("## parallel-search routing", 1)[1].split("## ", 1)[0]
        self.assertIn("default for general public-web discovery", section)
        self.assertNotIn("are the fallback", section)
        self.assertNotIn("google_search", section)

    def test_startup_skills_defer_to_shared_source_selection(self):
        for name in ("context-mode", "context7"):
            with self.subTest(skill=name):
                text = (REPO_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("source-selection table in `AGENTS.md`", text)
                self.assertIn("parallel-search `web_search`", text)
                self.assertNotIn("## Tool selection order", text)

    def test_code_mode_and_reviewer_exceptions_remain_explicit(self):
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn('search({ namespace: "parallel-search", limit: 2 })', text)
        self.assertIn("Catalog search discovers tools; it does not search the web", text)
        self.assertIn("These seven agents do not retrieve sources or load skills", text)


if __name__ == "__main__":
    unittest.main()

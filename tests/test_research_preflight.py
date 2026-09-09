"""Phase 1 behavior against real temporary Git indexes; no model/network calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.research_preflight import assess, private_state_path, template_errors, portal_skills


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "repo"
        self.root.mkdir()
        self.git("init", "--quiet")
        self.public = b"Name: [YOUR_NAME]\n"
        (self.root / "CLAUDE.md").write_bytes(self.public)
        (self.root / ".gitignore").write_text("private/\n")
        (self.root / "research-template-manifest.json").write_text(json.dumps({
            "schema_version": 1,
            "files": {"CLAUDE.md": [hashlib.sha256(self.public).hexdigest()]}}))
        self.git("add", "CLAUDE.md", ".gitignore")
        self.env = {"AI_JOB_RADAR_HOME": str(self.base / "private-state")}

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def run_action(self, mode="research", action="status"):
        return assess(self.root, mode, action, self.env)

    def test_research_needs_no_profile_setup_or_state(self):
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        result = self.run_action(action="configure")
        self.assertEqual(result["status"], "ready_for_gated_research")
        self.assertFalse(Path(result["state_path"]).exists())
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")))
        self.assertFalse(result["extraction"]["enabled"])
        self.assertEqual(result["sources_enabled"], [])

    def test_setup_and_section_update_cannot_enter_profile_generation(self):
        for action in ["setup", "profile-write", "configure"]:
            result = self.run_action("application", action)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("public_template_profile_write_blocked", result["blockers"])
        self.assertEqual((self.root / "CLAUDE.md").read_bytes(), self.public)

    def test_block_unimplemented_research_without_application_fallback(self):
        for action in ["outcome", "export"]:
            result = self.run_action(action=action)
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["canonical_spec"], ".claude/skills/research/SKILL.md")

    def test_execution_readiness_does_not_create_state_or_assert_qualification(self):
        for action in ["collect", "analyze", "refresh", "brief"]:
            result = self.run_action(action=action)
            self.assertEqual(result["status"], "ready_for_gated_research")
            self.assertFalse(result["extraction"]["enabled"])
            self.assertFalse(Path(result["state_path"]).exists())

    def test_import_readiness_does_not_enable_collection_or_create_state(self):
        result = self.run_action(action="import")
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["phase_2"]["reviewed_local_import"], "available_with_supported_policy")
        self.assertEqual(result["sources_enabled"], [])
        self.assertFalse(Path(result["state_path"]).exists())

    def test_application_status_keeps_its_own_route(self):
        self.assertEqual(self.run_action("application")["canonical_spec"], ".claude/")

    def test_personal_data_with_placeholder_still_present_is_rejected(self):
        (self.root / "CLAUDE.md").write_bytes(self.public + b"Private detail: synthetic-secret\n")
        errors = template_errors(self.root)
        self.assertTrue(errors)
        self.assertNotIn("synthetic-secret", " ".join(errors))

    def test_staged_personal_data_is_detected_after_worktree_restoration(self):
        (self.root / "CLAUDE.md").write_bytes(b"Private person\n")
        self.git("add", "CLAUDE.md")
        (self.root / "CLAUDE.md").write_bytes(self.public)
        self.assertTrue(any("staged template" in e for e in template_errors(self.root)))

    def test_gitignore_does_not_make_tracked_content_private(self):
        (self.root / "private").mkdir()
        (self.root / "private/profile.json").write_text('{"synthetic":true}')
        self.git("add", "--force", "private/profile.json")
        self.assertTrue(any("still tracked" in e for e in template_errors(self.root)))

    def test_state_cannot_overlap_checkout_or_escape_via_symlink(self):
        alias = self.base / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        for path in [str(self.root), str(self.root / "state"), str(self.base),
                     str(alias / "state"), "relative/path", ""]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                private_state_path(self.root, {"AI_JOB_RADAR_HOME": path})

    def test_missing_manifest_or_template_fails_closed(self):
        (self.root / "research-template-manifest.json").unlink()
        self.assertEqual(self.run_action()["status"], "blocked")

    def test_research_pointer_is_not_discovered_as_portal(self):
        for name in ["research", "sample-search"]:
            folder = self.root / ".agents/skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text("synthetic skill")
        cli = self.root / ".agents/skills/sample-search/cli"
        (cli / "src").mkdir(parents=True)
        (cli / "package.json").write_text("{}")
        (cli / "src/cli.ts").write_text("// fixture")
        self.assertEqual(portal_skills(self.root), ["sample-search"])


if __name__ == "__main__":
    unittest.main()

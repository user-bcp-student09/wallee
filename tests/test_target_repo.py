"""Selección del repositorio de destino y copia de output/."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from crew.target_repo import (
    copy_output,
    list_participant_dirs,
    list_repo_dirs,
    select_target_repo,
)


class TargetRepoTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.docs = Path(tmp.name) / "Documents"
        for name in (
            "T52415-Samuel-Luis-Mendoza",
            "T27757-luis-rodolfo-perez-soriano",
            "u17721-gladys-patino-abanto",
            "Zoom",
            "Visual Studio 2022",
        ):
            (self.docs / name).mkdir(parents=True)
        self.mine = self.docs / "T52415-Samuel-Luis-Mendoza"
        for name in ("ai-labs", "crewai", "wallee", ".workshop-bootstrap-cache"):
            (self.mine / name).mkdir()
        (self.mine / "PLAN.md").write_text("x")

    def test_only_participant_like_folders_are_listed(self):
        names = [p.name for p in list_participant_dirs(self.docs)]
        self.assertEqual(
            names,
            ["T27757-luis-rodolfo-perez-soriano", "T52415-Samuel-Luis-Mendoza", "u17721-gladys-patino-abanto"],
        )

    def test_repo_listing_skips_hidden_files_and_source_repo(self):
        names = [p.name for p in list_repo_dirs(self.mine, exclude=self.mine / "wallee")]
        self.assertEqual(names, ["ai-labs", "crewai"])

    def test_interactive_selection(self):
        answers = iter(["x", "2", "9", "2"])
        with mock.patch.dict("os.environ", {"WALLEE_DOCUMENTS_DIR": str(self.docs)}, clear=False), \
                mock.patch.dict("os.environ", {"WALLEE_TARGET_REPO": ""}):
            target = select_target_repo(self.mine / "wallee", ask=lambda _: next(answers))
        self.assertEqual(target, self.mine / "crewai")

    def test_copy_output_merges_and_skips_checkpoint_and_node_modules(self):
        out = self.docs / "out"
        (out / "specs").mkdir(parents=True)
        (out / "specs" / "a.md").write_text("new")
        (out / ".checkpoint.json").write_text("{}")
        (out / "frontend-react" / "node_modules" / "pkg").mkdir(parents=True)
        (out / "frontend-react" / "node_modules" / "pkg" / "i.js").write_text("x")
        target = self.mine / "crewai"
        (target / "specs").mkdir()
        (target / "specs" / "a.md").write_text("old")

        copied = copy_output(out, target)

        self.assertEqual(copied, [Path("specs/a.md")])
        self.assertEqual((target / "specs" / "a.md").read_text(), "new")
        self.assertFalse((target / ".checkpoint.json").exists())
        self.assertFalse((target / "frontend-react").exists())


if __name__ == "__main__":
    unittest.main()

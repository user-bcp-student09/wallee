"""Publicación: commit, push y PR con preaprobación, usando git real contra un remoto local y gh simulado."""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from crew import publish

FEATURE = {"title": "Transfer funds", "description": "d", "acceptance_criteria": []}
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def sh(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.remote, self.repo = root / "remote.git", root / "repo"
        sh(root, "init", "--bare", "-b", "main", str(self.remote))
        self.repo.mkdir()
        sh(self.repo, "init", "-b", "main")
        sh(self.repo, "remote", "add", "origin", str(self.remote))
        env = patch.dict(os.environ, GIT_ENV)
        env.start()
        self.addCleanup(env.stop)
        (self.repo / "README.md").write_text("base", encoding="utf-8")
        sh(self.repo, "add", ".")
        sh(self.repo, "commit", "-m", "init")
        sh(self.repo, "push", "-u", "origin", "main")
        self.calls = []

        def fake_gh(repo, *args, input=None):
            if args[0] == "repo":
                return "main"
            self.calls.append((args, input))
            return "https://github.com/o/r/pull/7"

        for p in (patch.object(publish, "gh", fake_gh), patch.object(publish, "gh_available", return_value=True),
                  contextlib.redirect_stdout(io.StringIO())):
            p.__enter__()
            self.addCleanup(p.__exit__, None, None, None)

    def write(self, *relatives):
        for relative in relatives:
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x", encoding="utf-8")
        return [Path(r) for r in relatives]

    def run_publish(self, files, answers, **kwargs):
        replies = iter(answers)
        return publish.publish_output(self.repo, files, FEATURE, ["QA & Security"], "w1-demo",
                                      ["QA & Security"], ask=lambda _: next(replies), **kwargs)

    def test_pushes_branch_and_opens_pr_after_approval(self):
        files = self.write("test/a.spec.ts", "security/review.md")
        url = self.run_publish(files, ["", "s"])
        self.assertEqual(url, "https://github.com/o/r/pull/7")
        branch = sh(self.repo, "branch", "--show-current")
        self.assertEqual(branch, "wallee/qa-security-transfer-funds")
        self.assertIn(branch, sh(self.repo, "ls-remote", "--heads", "origin"))
        self.assertEqual(sh(self.repo, "show", "--name-only", "--format=", "HEAD").splitlines(),
                         ["security/review.md", "test/a.spec.ts"])
        args, body = self.calls[0]
        self.assertEqual(args[:2], ("pr", "create"))
        self.assertEqual(args[args.index("--base") + 1], "main")
        self.assertEqual(args[args.index("--head") + 1], branch)
        self.assertNotIn("--draft", args)
        self.assertIn("w1-demo", body)
        self.assertIn("`test/a.spec.ts`", body)

    def test_asks_pr_repo_defaults_and_remembers_it(self):
        saved = []
        self.run_publish(self.write("test/a.spec.ts"), ["", "s"], on_pr_repo=saved.append)
        args, _ = self.calls[0]
        self.assertEqual(args[args.index("--repo") + 1], "user-bcp-student17/wallee-app")
        self.assertEqual(saved, ["user-bcp-student17/wallee-app"])

    def test_custom_and_saved_pr_repo_from_fork_origin(self):
        sh(self.repo, "remote", "set-url", "origin", "https://github.com/ntt6/wallee-app.git")
        real = publish.git

        def fake_git(repo, *args, **kw):
            return "" if args[:1] == ("push",) else real(repo, *args, **kw)

        with patch.object(publish, "git", fake_git):
            self.run_publish(self.write("test/a.spec.ts"), ["https://github.com/Otro/repo-x", "s"], pr_repo="a/b")
        args, _ = self.calls[0]
        self.assertEqual(args[args.index("--repo") + 1], "Otro/repo-x")
        self.assertEqual(args[args.index("--head") + 1], "ntt6:wallee/qa-security-transfer-funds")

    def test_invalid_pr_repo_is_asked_again_and_saved_one_is_the_default(self):
        saved = []
        self.run_publish(self.write("test/a.spec.ts"), ["no valido", "", "s"], pr_repo="a/b", on_pr_repo=saved.append)
        args, _ = self.calls[0]
        self.assertEqual(args[args.index("--repo") + 1], "a/b")
        self.assertEqual(saved, ["a/b"])

    def test_parse_github_repo(self):
        for value, expected in (("o/r", "o/r"), ("https://github.com/o/r.git", "o/r"), ("git@github.com:o/r.git", "o/r"),
                                ("https://github.com/o/r/", "o/r"), ("C:\\x\\remote.git", None), ("/tmp/a/b.git", None)):
            self.assertEqual(publish.parse_github_repo(value), expected)

    def test_rejecting_preapproval_pushes_but_creates_no_pr(self):
        url = self.run_publish(self.write("test/a.spec.ts"), ["", "n"])
        self.assertIsNone(url)
        self.assertEqual(self.calls, [])
        self.assertIn("wallee/", sh(self.repo, "ls-remote", "--heads", "origin"))

    def test_draft_and_title_edit(self):
        url = self.run_publish(self.write("test/a.spec.ts"), ["", "d", "e", "Mi título", "s"])
        self.assertTrue(url)
        args, _ = self.calls[0]
        self.assertIn("--draft", args)
        self.assertEqual(args[args.index("--title") + 1], "Mi título")

    def test_template_is_preserved_and_existing_branch_is_reused(self):
        (self.repo / ".github").mkdir()
        (self.repo / ".github" / "pull_request_template.md").write_text("## Qué cambia\n- [ ] Probado", encoding="utf-8")
        sh(self.repo, "checkout", "-b", "mi-rama")
        self.run_publish(self.write("test/a.spec.ts"), ["", "s"])
        self.assertEqual(sh(self.repo, "branch", "--show-current"), "mi-rama")
        args, body = self.calls[0]
        self.assertTrue(body.startswith("## Qué cambia\n- [ ] Probado"))
        self.assertEqual(args[args.index("--head") + 1], "mi-rama")

    def test_nothing_to_publish_and_non_git_target(self):
        self.assertIsNone(self.run_publish([Path("README.md")], []))
        with tempfile.TemporaryDirectory() as plain:
            self.assertIsNone(publish.publish_output(Path(plain), [Path("a")], FEATURE, ["QA & Security"]))
        self.assertEqual(self.calls, [])

    def test_missing_gh_and_opt_out_do_nothing(self):
        files = self.write("test/a.spec.ts")
        with patch.object(publish, "gh_available", return_value=False):
            self.assertIsNone(self.run_publish(files, []))
        self.assertEqual(sh(self.repo, "branch", "--show-current"), "main")
        with patch.dict(os.environ, {"WALLEE_PUBLISH": "false"}):
            self.assertIsNone(self.run_publish(files, []))
        self.assertEqual(self.calls, [])

    def test_body_lists_approved_steps_and_caps_files(self):
        body = publish.build_pr_body(FEATURE, ["QA & Security"], None, [f"f{i}.ts" for i in range(45)], ["QA & Security"])
        self.assertIn("- [x] QA & Security", body)
        self.assertIn("y 5 archivos más", body)
        self.assertIn("Cambio OpenSpec:** ninguno", body)


if __name__ == "__main__":
    unittest.main()

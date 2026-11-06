"""Los informes de QA acumulan una sección por feature en el repo destino en vez de sobrescribirse."""

from pathlib import Path
import tempfile
import unittest

from crew.qa_sections import has_section, is_accumulating, merge_section, reset_qa_documents
from crew.target_repo import copy_output

W1 = ("w1-1-andamiaje", "[W1] 1. Andamiaje")
W2 = ("w2-1-base", "[W2] 1. Base")


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class SectionTests(unittest.TestCase):
    def test_new_sections_are_appended_and_existing_ones_replaced_in_place(self):
        text = merge_section("", W1[0], W1[1], "resultado W1 v1")
        text = merge_section(text, W2[0], W2[1], "resultado W2")
        text = merge_section(text, W1[0], W1[1], "resultado W1 v2")

        self.assertIn("resultado W1 v2", text)
        self.assertNotIn("resultado W1 v1", text)
        self.assertIn("resultado W2", text)
        self.assertLess(text.index("[W1] 1. Andamiaje"), text.index("[W2] 1. Base"))
        self.assertEqual(text.count("wallee-qa:begin"), 2)

    def test_content_without_markers_is_preserved(self):
        text = merge_section("# Evidencia previa\n\nfila manual", W1[0], W1[1], "nuevo")
        self.assertTrue(text.startswith("# Evidencia previa\n\nfila manual"))
        self.assertTrue(has_section(text, W1[0]))
        self.assertFalse(has_section(text, W2[0]))

    def test_only_qa_markdown_documents_accumulate(self):
        for rel in ("specs/qa_security_report.md", "test/evidence.md", "security/security-review.md"):
            self.assertTrue(is_accumulating(Path(rel)), rel)
        for rel in ("test/onboarding.e2e-spec.ts", "specs/architect_report.md", "backend/src/a.md"):
            self.assertFalse(is_accumulating(Path(rel)), rel)


class CopyOutputTests(unittest.TestCase):
    def run_feature(self, output: Path, target: Path, section, report: str, **kwargs):
        reset_qa_documents(output)
        write(output, "specs/qa_security_report.md", report)
        write(output, "test/evidence.md", f"evidencia {section[0]}")
        write(output, "test/feature.e2e-spec.ts", f"// {section[0]}")
        write(output, "specs/architect_report.md", "arquitecto")
        return copy_output(output, target, section, **kwargs)

    def test_second_feature_adds_and_rerunning_the_first_updates_only_its_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, target = Path(tmp) / "output", Path(tmp) / "app"
            target.mkdir()
            self.run_feature(output, target, W1, "informe W1 v1")
            self.run_feature(output, target, W2, "informe W2")
            report = (target / "specs" / "qa_security_report.md").read_text(encoding="utf-8")
            self.assertIn("informe W1 v1", report)
            self.assertIn("informe W2", report)

            self.run_feature(output, target, W1, "informe W1 v2 verificado")
            report = (target / "specs" / "qa_security_report.md").read_text(encoding="utf-8")
            evidence = (target / "test" / "evidence.md").read_text(encoding="utf-8")
            self.assertIn("informe W1 v2 verificado", report)
            self.assertNotIn("informe W1 v1", report)
            self.assertIn("informe W2", report)
            self.assertIn("evidencia w1-1-andamiaje", evidence)
            self.assertIn("evidencia w2-1-base", evidence)
            self.assertEqual(report.count("wallee-qa:begin"), 2)
            # lo que no es un informe de QA se sigue copiando tal cual
            self.assertEqual((target / "specs" / "architect_report.md").read_text(encoding="utf-8"), "arquitecto")

    def test_declined_run_keeps_the_existing_section_but_adds_a_missing_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, target = Path(tmp) / "output", Path(tmp) / "app"
            target.mkdir()
            self.run_feature(output, target, W1, "W1 con resultados reales")
            self.run_feature(output, target, W1, "W1 borrador NO EJECUTADO", replace_qa_section=False)
            self.run_feature(output, target, W2, "W2 borrador NO EJECUTADO", replace_qa_section=False)
            report = (target / "specs" / "qa_security_report.md").read_text(encoding="utf-8")
            self.assertIn("W1 con resultados reales", report)
            self.assertNotIn("W1 borrador", report)
            self.assertIn("W2 borrador NO EJECUTADO", report)

    def test_without_a_section_files_are_overwritten_as_before(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, target = Path(tmp) / "output", Path(tmp) / "app"
            target.mkdir()
            write(output, "specs/qa_security_report.md", "nuevo")
            write(target, "specs/qa_security_report.md", "viejo")
            copy_output(output, target)
            self.assertEqual((target / "specs" / "qa_security_report.md").read_text(encoding="utf-8"), "nuevo")


if __name__ == "__main__":
    unittest.main()

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/specs/phase-14-email-render-matrix.md"
PACKAGE_PATH = ROOT / "tools/email_render_matrix/package.json"
SCHEMA_PATH = ROOT / "tools/email_render_matrix/report.schema.json"
SCRIPT_PATH = ROOT / "tools/email_render_matrix/render_matrix.cjs"


class EmailRenderMatrixContractTests(unittest.TestCase):
    def test_phase_spec_keeps_browser_and_email_client_evidence_separate(self):
        spec = SPEC_PATH.read_text(encoding="utf-8")
        self.assertIn("browser-preview-only", SCRIPT_PATH.read_text(encoding="utf-8"))
        self.assertIn("Never label browser previews as email-client certification", spec)
        self.assertIn("Outlook Word-engine emulation", spec)

    def test_playwright_dependency_and_report_contract_are_pinned(self):
        package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(package["devDependencies"]["playwright"], "1.62.1")
        self.assertEqual(schema["properties"]["scope"]["const"], "browser-preview-only")
        self.assertEqual(schema["properties"]["human_review"]["const"], "pending")

    def test_matrix_declares_four_stable_viewport_modes(self):
        script = SCRIPT_PATH.read_text(encoding="utf-8")
        for mode in ("desktop-light", "mobile-light", "desktop-dark", "mobile-dark"):
            self.assertIn(mode, script)
        self.assertIn("horizontal_overflow_px", script)
        self.assertIn("broken_images", script)


if __name__ == "__main__":
    unittest.main()

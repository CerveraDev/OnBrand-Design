import json
import hashlib
from email import policy
from email.parser import BytesParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/specs/phase-14-email-render-matrix.md"
PACKAGE_PATH = ROOT / "tools/email_render_matrix/package.json"
SCHEMA_PATH = ROOT / "tools/email_render_matrix/report.schema.json"
SCRIPT_PATH = ROOT / "tools/email_render_matrix/render_matrix.cjs"
EML_SCRIPT_PATH = ROOT / "tools/email_render_matrix/build_native_test_eml.py"
EVIDENCE_PATH = ROOT / "docs/evals/render-matrix/rider-wellness-v1"


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

    def test_rider_evidence_is_hash_bound_and_passes_browser_checks(self):
        report = json.loads((EVIDENCE_PATH / "render-report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["passed"])
        self.assertEqual(report["scope"], "browser-preview-only")
        self.assertEqual(report["human_review"], "pending")
        self.assertEqual(report["input"]["sha256"], "fcd0bed5e6ea6c5c2ca46ef76a130ecf0e3fee8c29f80cd8ecd9fcd4b867ad32")
        self.assertEqual([item["id"] for item in report["matrix"]], [
            "desktop-light",
            "mobile-light",
            "desktop-dark",
            "mobile-dark",
        ])
        for item in report["matrix"]:
            screenshot = EVIDENCE_PATH / item["screenshot"]["filename"]
            self.assertEqual(hashlib.sha256(screenshot.read_bytes()).hexdigest(), item["screenshot"]["sha256"])
            self.assertTrue(item["passed"])
            self.assertEqual(item["diagnostics"]["horizontal_overflow_px"], 0)
            self.assertEqual(item["diagnostics"]["image_count"], item["diagnostics"]["loaded_image_count"])
            self.assertEqual(item["request_failures"], [])
            self.assertEqual(item["page_errors"], [])
            self.assertEqual(item["console_errors"], [])
        by_id = {item["id"]: item for item in report["matrix"]}
        self.assertEqual(by_id["desktop-light"]["screenshot"]["sha256"], by_id["desktop-dark"]["screenshot"]["sha256"])
        self.assertEqual(by_id["mobile-light"]["screenshot"]["sha256"], by_id["mobile-dark"]["screenshot"]["sha256"])

    def test_native_message_builder_embeds_packaged_images_by_cid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "campaign"
            html_dir = package / "html"
            image_dir = package / "images"
            html_dir.mkdir(parents=True)
            image_dir.mkdir()
            html_path = html_dir / "test.html"
            html_path.write_text(
                '<html><body><img src="../images/pixel.gif"></body></html>',
                encoding="utf-8",
            )
            image_bytes = b"GIF89a"
            (image_dir / "pixel.gif").write_bytes(image_bytes)
            output_path = package / "test.eml"

            result = subprocess.run(
                [
                    sys.executable,
                    str(EML_SCRIPT_PATH),
                    "--html",
                    str(html_path),
                    "--from-address",
                    "sender@example.com",
                    "--to-address",
                    "recipient@example.com",
                    "--subject",
                    "Native test",
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            message = BytesParser(policy=policy.default).parsebytes(output_path.read_bytes())
            html_part = message.get_body(preferencelist=("html",))
            self.assertIsNotNone(html_part)
            self.assertIn("cid:onbrand-", html_part.get_content())
            self.assertNotIn("../images/", html_part.get_content())
            related = [part for part in message.walk() if part.get_content_disposition() == "inline"]
            self.assertEqual(len(related), 1)
            self.assertEqual(related[0].get_filename(), "pixel.gif")
            self.assertEqual(related[0].get_payload(decode=True), image_bytes)

            receipt = json.loads(output_path.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["transport_reference_change"], "../images/<name> -> cid:<content-id>")
            self.assertEqual(receipt["embedded_images"][0]["sha256"], hashlib.sha256(image_bytes).hexdigest())
            self.assertEqual(receipt["eml_sha256"], hashlib.sha256(output_path.read_bytes()).hexdigest())

    def test_native_message_builder_rejects_missing_packaged_images(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "campaign"
            html_dir = package / "html"
            html_dir.mkdir(parents=True)
            html_path = html_dir / "test.html"
            html_path.write_text(
                '<html><body><img src="../images/missing.png"></body></html>',
                encoding="utf-8",
            )
            output_path = package / "test.eml"

            result = subprocess.run(
                [
                    sys.executable,
                    str(EML_SCRIPT_PATH),
                    "--html",
                    str(html_path),
                    "--from-address",
                    "sender@example.com",
                    "--to-address",
                    "recipient@example.com",
                    "--subject",
                    "Native test",
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing packaged image(s): missing.png", result.stderr)
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()

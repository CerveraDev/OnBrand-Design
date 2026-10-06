from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path
import tempfile
import unittest

from tools.graph_mail.auth import load_env_file, update_env_file
from tools.graph_mail.send_mime import inspect_message, prepare_mime_bytes


class GraphMailTests(unittest.TestCase):
    def test_prepare_removes_only_unsent_header(self):
        raw = (
            b"From: sender@example.com\r\nTo: recipient@example.com\r\n"
            b"Subject: Test\r\nX-Unsent: 1\r\nX-Other: retained\r\n\r\nbody"
        )
        prepared = prepare_mime_bytes(raw)
        self.assertNotIn(b"X-Unsent", prepared)
        self.assertIn(b"X-Other: retained", prepared)
        self.assertIn(b"\r\n\r\nbody", prepared)

    def test_inspection_reports_vml_and_rejectable_background_cid(self):
        message = EmailMessage(policy=SMTP)
        message["From"] = "sender@example.com"
        message["To"] = "recipient@example.com"
        message["Subject"] = "Native test"
        message.set_content("fallback")
        message.add_alternative(
            '<html><body><table background="cid:bg">'
            '<!--[if gte mso 9]><v:rect data-onbrand-background="true">'
            '<v:fill src="cid:bg" /></v:rect><![endif]--></table></body></html>',
            subtype="html",
        )
        details = inspect_message(message.as_bytes())
        self.assertEqual(details["from"], "sender@example.com")
        self.assertEqual(details["to"], ["recipient@example.com"])
        self.assertEqual(details["bulletproof_backgrounds"], 1)
        self.assertTrue(details["background_cid_present"])

    def test_env_update_preserves_fields_and_uses_private_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ".env"
            path.write_text("ONBRAND_GRAPH_CLIENT_ID=client\nONBRAND_GRAPH_REFRESH_TOKEN=old\n")
            update_env_file(path, {"ONBRAND_GRAPH_REFRESH_TOKEN": "new"})
            _, values = load_env_file(path)
            self.assertEqual(values["ONBRAND_GRAPH_CLIENT_ID"], "client")
            self.assertEqual(values["ONBRAND_GRAPH_REFRESH_TOKEN"], "new")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()

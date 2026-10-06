import unittest

from tools.rider_campaign_runtime.email_compat import (
    add_bulletproof_backgrounds,
    bulletproof_background_counts,
)


class BulletproofBackgroundTests(unittest.TestCase):
    def test_cover_background_gets_legacy_attribute_and_vml(self):
        html = (
            '<table class="row-content" width="600" style="background-color: #ffffff; '
            "background-image: url('image.jpg'); background-repeat: no-repeat; "
            'background-size: cover; border-left: 20px solid #fff; border-right: 20px solid #fff;">'
            '<tbody><tr><td><div style="height:370px">x</div></td></tr></tbody></table>'
        )

        rewritten, count = add_bulletproof_backgrounds(html)

        self.assertEqual(count, 1)
        self.assertIn('background="image.jpg"', rewritten)
        self.assertIn('<!--[if gte mso 9]>\n<v:rect', rewritten)
        self.assertNotIn('<!--[if gte mso 9]><!--', rewritten)
        self.assertIn('style="width:560px;"', rewritten)
        self.assertIn('<v:fill type="frame" aspect="atleast" src="image.jpg" color="#ffffff" />', rewritten)
        self.assertIn('mso-fit-shape-to-text:true', rewritten)
        self.assertEqual(bulletproof_background_counts(rewritten), (1, 1))
        self.assertEqual(add_bulletproof_backgrounds(rewritten), (rewritten, 0))

    def test_repeating_texture_is_not_wrapped(self):
        html = (
            '<table width="600" style="background-image: url(\'spacer.gif\'); '
            'background-repeat: repeat;"><tr><td>x</td></tr></table>'
        )

        rewritten, count = add_bulletproof_backgrounds(html)

        self.assertEqual(count, 0)
        self.assertEqual(rewritten, html)
        self.assertEqual(bulletproof_background_counts(rewritten), (0, 0))

    def test_empty_background_is_not_wrapped(self):
        html = (
            '<table width="600" style="background-image: url(\'\'); '
            'background-repeat: no-repeat;"><tr><td>x</td></tr></table>'
        )

        rewritten, count = add_bulletproof_backgrounds(html)

        self.assertEqual(count, 0)
        self.assertEqual(rewritten, html)


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch, Mock

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "daily_news"))
import build
import collect_news
import publish
import public_media
from PIL import Image
from requests_hardened.ip_filter import InvalidIPAddress


class PipelineTests(unittest.TestCase):
    def test_public_fetch_refuses_non_http_and_private_targets(self):
        with self.assertRaises(ValueError):
            public_media.fetch_public("file:///example.png", limit=20, timeout=1)
        with patch("requests.adapters.HTTPAdapter.proxy_manager_for") as proxy:
            with self.assertRaises(InvalidIPAddress):
                public_media.fetch_public("https://127.0.0.1/image", limit=20, timeout=1)
            proxy.assert_not_called()

    def test_size_limit_and_redirect_validation(self):
        redirect = Mock(is_redirect=True, headers={"Location": "file:///example.png"})
        body = Mock(is_redirect=False)
        body.iter_content.return_value = [b"ab", b"cdef"]
        with patch.object(public_media.PUBLIC_WEB.__class__, "get_session", autospec=True) as get_session:
            session = get_session.return_value.__enter__.return_value
            session.merge_environment_settings.return_value = {"proxies": {}, "stream": True}
            response = session.get_adapter.return_value.send.return_value.__enter__
            response.return_value = redirect
            with self.assertRaises(ValueError):
                public_media.fetch_public("https://example.org/", limit=4, timeout=1)
            self.assertEqual(session.get_adapter.return_value.send.call_count, 1)
            response.return_value = body
            with self.assertRaises(ValueError):
                public_media.fetch_public("https://example.org/", limit=4, timeout=1)
            self.assertEqual(public_media.fetch_public("https://example.org/", limit=4, timeout=1, prefix=True), b"abcd")

    def test_article_enriched_once_across_feeds(self):
        xml = b"<rss><channel><item><title>News</title><link>https://example.org/story</link></item></channel></rss>"
        with TemporaryDirectory() as folder, patch.object(collect_news, "OUTPUT_FILE", os.path.join(folder, "news.json")), \
                patch.object(collect_news, "fetch_feed", return_value=xml), \
                patch.object(collect_news, "fetch_og_image", return_value="image") as image, \
                contextlib.redirect_stdout(io.StringIO()):
            collect_news.main()
            image.assert_called_once_with("https://example.org/story")
            self.assertEqual(json.loads(Path(collect_news.OUTPUT_FILE).read_text())["total_count"], 1)

    def test_card_crop_and_duplicate_themes(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "card.png"
            public_media.save_card_image(Image.new("RGB", (1000, 600)), path)
            with Image.open(path) as image:
                self.assertEqual(image.size, (1080, 702))
            card = {"theme": "business", "colors": {"bg": "#123456", "soft": "#654321", "ink": "#111111"}}
            build.generate_css({"cards": [card, card]}, folder)
            css = (Path(folder) / "style.css").read_text()
            for num in ("02", "03"):
                self.assertIn(f'.theme-business[data-card-number="{num}"]', css)
                self.assertIn(f"card_{num}_business.png", css)

    def test_cleanup_preserves_unpublished_files(self):
        with TemporaryDirectory() as folder, patch.object(publish, "SCRIPT_DIR", folder), \
                patch.object(publish, "HISTORY_PATH", os.path.join(folder, "history.json")):
            root = Path(folder) / "2026-11-21"
            root.mkdir()
            (root / "news_data.json").write_text(json.dumps({"date": root.name, "cards": [{"company": "A"}]}))
            args = ["publish.py", "--date", root.name, "--skip-instagram", "--skip-telegram", "--clean"]
            with patch.object(sys, "argv", args), patch.object(publish, "publish_threads", return_value=[]), \
                    self.assertRaises(SystemExit):
                publish.main()
            self.assertTrue(root.is_dir())
            with self.assertRaises(ValueError):
                public_media.build_date("invalid")

    def test_partial_retry_only_posts_missing_card(self):
        with TemporaryDirectory() as folder, patch.object(publish, "SCRIPT_DIR", folder), \
                patch.object(publish, "HISTORY_PATH", os.path.join(folder, "history.json")), \
                patch.object(publish, "get_threads_user_id", return_value="fixture-user"), \
                patch.object(publish.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
            root = Path(folder) / "2026-11-21"
            root.mkdir()
            card = {"company": "Same", "status": "reported", "title": "News", "body": "Body", "source": "Source"}
            (root / "news_data.json").write_text(json.dumps({"date": root.name, "cards": [card, card]}))
            args = ["publish.py", "--date", root.name, "--skip-instagram", "--skip-telegram"]
            with patch.object(sys, "argv", args), patch.object(publish, "create_and_publish_thread",
                    side_effect=["first", ValueError("temporary"), "second"]) as post:
                with self.assertRaises(SystemExit):
                    publish.main()
                self.assertTrue(publish.load_history()[0]["partial"])
                publish.main()
                publish.main()
                self.assertEqual(post.call_count, 3)
                history = publish.load_history()
                self.assertEqual(len(history), 1)
                self.assertFalse(history[0]["partial"])
                self.assertEqual([(r["index"], r["root_id"]) for r in history[0]["threads"]], [(0, "first"), (1, "second")])


if __name__ == "__main__":
    unittest.main()

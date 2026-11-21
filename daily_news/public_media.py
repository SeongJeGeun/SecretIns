"""Fetch public articles and images without using local credentials or private addresses."""

from datetime import date
from io import BytesIO
import os
import re
from tempfile import NamedTemporaryFile
from time import monotonic
from urllib.parse import urljoin, urlsplit

from PIL import Image
from requests import Request
from requests.utils import select_proxy
from requests_hardened import Config, Manager

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DailyNews/1.0)"}
PUBLIC_WEB = Manager(Config(ip_filter_enable=True, ip_filter_allow_loopback_ips=False,
                            never_redirect=True, default_timeout=(5, 15)))
ARTICLE_LIMIT = 4 * 1024 * 1024
IMAGE_LIMIT = 16 * 1024 * 1024


def build_date(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError("date must be YYYY-MM-DD")
    return value


def card_filenames(date, news_count):
    return [f"{date}_card_{i:02d}.png" for i in range(1, news_count + 3)]


def theme_name(value):
    if not isinstance(value, str) or not re.fullmatch("[a-z0-9_-]+", value):
        raise ValueError("Invalid card theme")
    return value


def fetch_public(url, *, limit, timeout, prefix=False):
    """Keep the first limit bytes for article previews, reject incomplete feeds and images."""
    deadline = monotonic() + timeout
    with PUBLIC_WEB.get_session() as session:
        for _ in range(6):
            parsed = urlsplit(url)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username is not None:
                raise ValueError("Expected a public HTTP(S) URL")
            # The adapter pins the checked IP and verifies TLS against the original hostname.
            # Follow redirects here to avoid buffering arbitrary redirect bodies in Requests.
            # Preparing directly avoids inheriting .netrc credentials for article hosts.
            request = Request("GET", url, headers=HEADERS).prepare()
            settings = session.merge_environment_settings(request.url, {}, True, None, None)
            if parsed.scheme == "http" and select_proxy(request.url, settings["proxies"]):
                raise ValueError("Use HTTPS for articles fetched through a proxy")
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise TimeoutError("Download timed out")
            with session.get_adapter(request.url).send(request, timeout=remaining, **settings) as response:
                if response.is_redirect:
                    url = urljoin(request.url, response.headers["Location"])
                    continue
                response.raise_for_status()
                body = bytearray()
                for chunk in response.iter_content(64 * 1024):
                    if monotonic() > deadline:
                        raise TimeoutError("Download timed out")
                    available = limit - len(body)
                    if len(chunk) > available:
                        if not prefix:
                            raise ValueError("Download exceeds size limit")
                        body.extend(chunk[:available])
                        break
                    body.extend(chunk)
                return body
        raise ValueError("Too many article redirects")


def open_web_image(url, timeout):
    data = fetch_public(url, limit=IMAGE_LIMIT, timeout=timeout)
    image = Image.open(BytesIO(data), formats=["JPEG", "PNG", "WEBP", "GIF", "AVIF", "TIFF", "BMP"])
    if image.width * image.height > 32_000_000:
        image.close()
        raise ValueError("Image exceeds pixel limit")
    return image


def save_card_image(image, out_path, width=1080, height=702):
    """Crop at the center and publish the complete PNG with a single rename."""
    ow, oh = image.size
    crop_w = min(ow, max(1, oh * width // height))
    crop_h = min(oh, max(1, ow * height // width))
    x, y = (ow - crop_w) // 2, (oh - crop_h) // 2
    crop = image.crop((x, y, x + crop_w, y + crop_h))
    result = crop.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    with NamedTemporaryFile(dir=os.path.dirname(out_path) or ".", delete=False) as tmp:
        try:
            result.save(tmp, "PNG")
            tmp.close()
            os.replace(tmp.name, out_path)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

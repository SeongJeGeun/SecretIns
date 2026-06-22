#!/usr/bin/env python3
"""
Daily IT & AI News Card News Builder
=====================================
news_data.json을 검증한 뒤 카드뉴스 HTML/CSS/PNG를 생성합니다.
"""

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from html import escape
from urllib.parse import urlparse

import requests
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "template")
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}

ALLOWED_STATUS = {"official", "reported"}
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
HANGUL_RE = re.compile(r"[가-힣]")
BROAD_PATHS = {
    "", "/", "/news", "/business", "/technology", "/tech", "/ai",
    "/artificial-intelligence", "/innovation", "/markets", "/world",
    "/section/technology", "/section/business",
}
BROAD_SEGMENTS = {
    "news", "business", "technology", "tech", "ai", "artificial-intelligence",
    "innovation", "markets", "world", "latest", "category", "section", "tag", "topics",
}


def is_valid_url(value):
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_broad_or_home_url(value):
    parsed = urlparse(value)
    path = parsed.path.rstrip("/")
    if path in BROAD_PATHS:
        return True
    segments = [s for s in path.split("/") if s]
    if not segments:
        return True
    if len(segments) == 1 and segments[0].lower() in BROAD_SEGMENTS:
        return True
    if len(segments) == 2 and all(s.lower() in BROAD_SEGMENTS for s in segments):
        return True
    return False


def ensure_article_url(url, label):
    if not is_valid_url(url):
        raise ValueError(f"\n[유효성 검증 에러] {label} URL 형식이 올바르지 않습니다: {url!r}")
    if is_broad_or_home_url(url):
        raise ValueError(
            f"\n[유효성 검증 에러] {label}는 홈/섹션 URL이 아니라 실제 기사·공식 발표 상세 URL이어야 합니다.\n"
            f"  - 현재 URL: {url}"
        )


def validate_threads(card, comp, allow_korean_threads):
    threads = card.get("threads")
    if threads is None:
        return
    if not isinstance(threads, dict):
        raise ValueError(f"\n[유효성 검증 에러] {comp} 카드의 'threads' 필드는 객체여야 합니다.")

    values = []
    for field in ["hook", "detail", "question"]:
        value = threads.get(field, "")
        if value and not isinstance(value, str):
            raise ValueError(f"\n[유효성 검증 에러] {comp} threads.{field} 값은 문자열이어야 합니다.")
        values.append(value)

    poll_options = threads.get("poll_options", [])
    if poll_options:
        if not isinstance(poll_options, list):
            raise ValueError(f"\n[유효성 검증 에러] {comp} threads.poll_options 값은 배열이어야 합니다.")
        for option in poll_options:
            if not isinstance(option, str):
                raise ValueError(f"\n[유효성 검증 에러] {comp} threads.poll_options 값은 문자열 배열이어야 합니다.")
            if len(option) > 25:
                raise ValueError(f"\n[유효성 검증 에러] {comp} poll option이 너무 깁니다: {option}")
        values.extend(poll_options)

    full_text = "\n".join(values).strip()
    if full_text and len(full_text) > 490:
        raise ValueError(f"\n[유효성 검증 에러] {comp} Threads 본문이 490자를 초과합니다.")
    if full_text and not allow_korean_threads and HANGUL_RE.search(full_text):
        raise ValueError(
            f"\n[유효성 검증 에러] {comp} Threads 문구에 한국어가 포함되어 있습니다.\n"
            "  - 한국어 Threads를 허용하려면 --allow-korean-threads 옵션을 사용하세요."
        )


def validate_news_data(data, allow_korean_threads=False, allow_wikimedia_fallback=False):
    if not isinstance(data, dict):
        raise ValueError("\n[유효성 검증 에러] news_data.json 최상위 값은 객체여야 합니다.")
    for field in ["date", "cards"]:
        if field not in data:
            raise ValueError(f"\n[유효성 검증 에러] 최상위 필드 누락: {field}")

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except Exception as exc:
        raise ValueError(f"\n[유효성 검증 에러] date는 YYYY-MM-DD 형식이어야 합니다: {data.get('date')!r}") from exc

    mode = data.get("mode", "daily")
    if mode not in {"daily", "event"}:
        raise ValueError(f"\n[유효성 검증 에러] mode 값은 daily 또는 event여야 합니다: {mode!r}")

    cards = data.get("cards")
    if not isinstance(cards, list) or not cards:
        raise ValueError("\n[유효성 검증 에러] cards는 비어 있지 않은 배열이어야 합니다.")

    event_release_times = {"wwdc": datetime(2026, 6, 9, 2, 0, 0)}
    event_title = data.get("event_title", "")
    current_time = datetime.now()
    for event_key, release_time in event_release_times.items():
        matched = event_key in event_title.lower() or any(
            event_key in c.get("title", "").lower()
            or event_key in c.get("body", "").lower()
            or event_key in c.get("image_search", "").lower()
            for c in cards
        )
        if matched and current_time < release_time:
            official_cards = [c for c in cards if c.get("status") == "official"]
            if official_cards:
                titles = ", ".join(f"'{c.get('title')}'" for c in official_cards)
                raise ValueError(
                    f"\n[유효성 검증 에러] 아직 공식 발표 전인 이벤트 뉴스가 'official'로 표기되었습니다.\n"
                    f"  - 대상 이벤트: {event_key.upper()}\n"
                    f"  - 발표 예정 시간: {release_time:%Y-%m-%d %H:%M:%S} KST\n"
                    f"  - 현재 시스템 시간: {current_time:%Y-%m-%d %H:%M:%S} KST\n"
                    f"  - 오류 카드: {titles}"
                )

    required_card = ["company", "title", "body", "source", "status", "theme", "colors"]
    for idx, card in enumerate(cards, start=1):
        if not isinstance(card, dict):
            raise ValueError(f"\n[유효성 검증 에러] Card {idx}는 객체여야 합니다.")
        comp = card.get("company", f"Card {idx}")

        for field in required_card:
            if field not in card:
                raise ValueError(f"\n[유효성 검증 에러] {comp} 카드 필드 누락: {field}")
        for field in ["company", "title", "body", "source", "theme"]:
            if not isinstance(card.get(field), str) or not card.get(field).strip():
                raise ValueError(f"\n[유효성 검증 에러] {comp} 카드의 {field} 값은 비어 있지 않은 문자열이어야 합니다.")
        if card["status"] not in ALLOWED_STATUS:
            raise ValueError(f"\n[유효성 검증 에러] {comp} status 값은 official/reported 중 하나여야 합니다.")
        if not re.match(r"^[a-z0-9_-]+$", card["theme"]):
            raise ValueError(f"\n[유효성 검증 에러] {comp} theme 값은 영문 소문자, 숫자, _, -만 허용됩니다.")

        colors = card.get("colors")
        if not isinstance(colors, dict):
            raise ValueError(f"\n[유효성 검증 에러] {comp} colors 값은 객체여야 합니다.")
        for key in ["bg", "soft", "ink"]:
            if not HEX_COLOR_RE.match(str(colors.get(key, ""))):
                raise ValueError(f"\n[유효성 검증 에러] {comp} colors.{key} 값은 #RRGGBB 형식이어야 합니다.")

        evidence_urls = []
        if card.get("source_url"):
            ensure_article_url(card["source_url"], f"{comp} source_url")
            evidence_urls.append(card["source_url"])

        related_urls = card.get("related_urls", [])
        if not isinstance(related_urls, list):
            raise ValueError(f"\n[유효성 검증 에러] {comp} related_urls 필드는 배열이어야 합니다.")
        for url in related_urls:
            ensure_article_url(url, f"{comp} related_urls")
            evidence_urls.append(url)

        if not evidence_urls:
            raise ValueError(
                f"\n[유효성 검증 에러] {comp} 카드에는 최소 1개의 실제 기사·공식 발표 상세 URL이 필요합니다."
            )

        image_url = card.get("image_url")
        if image_url:
            if not is_valid_url(image_url):
                raise ValueError(f"\n[유효성 검증 에러] {comp} image_url 형식이 올바르지 않습니다: {image_url!r}")
        elif not allow_wikimedia_fallback:
            # [수정] 하드 중단 대신 MISSING_IMAGE_TRIGGER 로그 출력 후 계속 진행
            # fuse_news.py 실패 시 AI가 이미지를 생성하고 image_url을 채워주는 흐름을 지원
            num = str(idx + 1).zfill(2)
            theme = card.get("theme", "unknown")
            print(
                f"[MISSING_IMAGE_TRIGGER] card_num={num}, theme={theme}, "
                f"company={comp}, title={card.get('title', '')}, "
                f"reason=no_image_url query={card.get('image_search', '')}"
            )

        validate_threads(card, comp, allow_korean_threads)
        print(f"  ✓ {comp} 검증 완료: evidence_urls={len(evidence_urls)}, image_url={'yes' if image_url else 'MISSING_TRIGGER_EMITTED'}")


def generate_html(data, output_dir):
    date = data["date"]
    date_display = date.replace("-", ".")
    cards = data["cards"]
    news_count = len(cards)

    if data.get("mode", "daily") == "event":
        cover_eyebrow = "Special Event Briefing"
        cover_title = data.get("event_title", "스페셜 이벤트")
    else:
        cover_eyebrow = "Daily IT &amp; AI Briefing"
        cover_title = "오늘의 IT 뉴스 브리핑"

    safe_date = escape(date)
    safe_date_display = escape(date_display)
    safe_cover_title = escape(cover_title)
    safe_cover_eyebrow = escape(cover_eyebrow)
    safe_sources = escape(", ".join(c["company"] for c in cards))

    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_date} {safe_cover_title}</title>
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <main class="deck" aria-label="{safe_date_display} {safe_cover_title} 카드뉴스">
    <section class="card card--thumbnail" id="card-01" data-card-number="01">
      <div class="cover-art" aria-hidden="true"></div>
      <div class="card-inner">
        <header class="topline">
          <span class="card-number">01</span>
          <span class="date">{safe_date_display}</span>
        </header>
        <div class="hero-copy">
          <p class="eyebrow">{safe_cover_eyebrow}</p>
          <h1>{safe_cover_title}</h1>
          <p class="subtitle">확인된 글로벌 IT/AI 핵심 소식 {news_count}개</p>
        </div>
        <div class="tag-row" aria-label="태그">
          <span>{news_count} NEWS</span><span>FACT CHECK</span><span>TECH TREND</span>
        </div>
        <p class="source-line">출처: 각 카드 하단 표기</p>
      </div>
    </section>
"""

    for idx, card in enumerate(cards, start=2):
        num = str(idx).zfill(2)
        status_class = "status--official" if card["status"] == "official" else "status--reported"
        status_text = "공식 확인" if card["status"] == "official" else "보도 기준"
        safe_theme = escape(card["theme"], quote=True)
        safe_company = escape(card["company"])
        safe_title = escape(card["title"])
        safe_body = escape(card["body"])
        safe_source = escape(card["source"])
        html += f"""
    <section class="card card--brief theme-{safe_theme}" id="card-{num}" data-card-number="{num}">
      <div class="visual-area" aria-hidden="true">
        <span class="image-badge">{safe_company} · {status_text}</span>
      </div>
      <div class="text-panel">
        <header class="brief-header">
          <span class="company">{safe_company}</span>
          <span class="status {status_class}">{status_text}</span>
        </header>
        <h2>{safe_title}</h2>
        <p>{safe_body}</p>
        <footer class="card-footer">{safe_source}</footer>
      </div>
    </section>
"""

    cta_num = str(news_count + 2).zfill(2)
    html += f"""
    <section class="card card--cta" id="card-{cta_num}" data-card-number="{cta_num}">
      <div class="cta-art" aria-hidden="true"></div>
      <div class="card-inner">
        <header class="topline">
          <span class="card-number">{cta_num}</span>
          <span class="date">{safe_date_display}</span>
        </header>
        <div class="cta-copy">
          <p class="eyebrow">Daily IT News</p>
          <h2>팔로우하고<br>내일 IT 뉴스 받기</h2>
          <p>오늘의 IT 뉴스 브리핑</p>
        </div>
        <div class="brand-row">
          <span class="brand-name">IT Media OS</span>
          <span class="brand-note">정확하게 확인된 IT 뉴스만 압축 정리</span>
        </div>
        <footer class="card-footer card-footer--cta">출처: {safe_sources} 공식 발표 및 주요 외신 보도 기준</footer>
      </div>
    </section>
  </main>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as fp:
        fp.write(html)
    print(f"  ✓ index.html 생성 ({news_count}개 뉴스 카드)")


def generate_css(data, output_dir):
    with open(os.path.join(TEMPLATE_DIR, "style.css"), "r", encoding="utf-8") as fp:
        base_css = fp.read()

    themes = "\n/* Themes - Auto-generated */\n"
    for idx, card in enumerate(data["cards"], start=2):
        num = str(idx).zfill(2)
        theme = card["theme"]
        colors = card["colors"]
        img = f"card_{num}_{theme}.png"
        themes += f""".theme-{theme} {{
  --theme-bg: {colors["bg"]};
  --theme-soft: {colors["soft"]};
  --theme-ink: {colors["ink"]};
  --image-bg: url("./assets/{img}") center / cover no-repeat;
}}

"""

    with open(os.path.join(output_dir, "style.css"), "w", encoding="utf-8") as fp:
        fp.write(base_css + themes)
    print("  ✓ style.css 생성 (베이스 + 테마)")


def search_wikimedia(query):
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query + " filetype:bitmap",
        "srnamespace": 6,
        "srlimit": 5,
    }
    try:
        res = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            results = res.json().get("query", {}).get("search", [])
            if results:
                return results[0]["title"].replace("File:", "")
    except Exception:
        return None
    return None


def wikimedia_url(filename):
    name = filename.replace(" ", "_")
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{name}"


def download_and_resize(url, out_path, w=1080, h=702):
    tmp = out_path + ".tmp"
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        if res.status_code != 200:
            print(f"    ✗ HTTP {res.status_code}")
            return False
        with open(tmp, "wb") as fp:
            fp.write(res.content)

        with Image.open(tmp) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            ow, oh = img.size
            if ow < 500 or oh < 300:
                print(f"    ✗ 이미지 해상도가 너무 낮습니다: {ow}x{oh}")
                return False
            target_ratio = w / h
            current_ratio = ow / oh
            if current_ratio > target_ratio:
                new_w = int(oh * target_ratio)
                left = (ow - new_w) // 2
                img = img.crop((left, 0, left + new_w, oh))
            else:
                new_h = int(ow / target_ratio)
                top = (oh - new_h) // 2
                img = img.crop((0, top, ow, top + new_h))
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            img.save(out_path, "PNG")
        print(f"    ✓ 저장 완료 ({w}x{h})")
        return True
    except Exception as exc:
        print(f"    ✗ 에러: {exc}")
        return False
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def download_images(data, output_dir, reuse_assets=False, allow_wikimedia_fallback=False):
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    missing_images = []

    template_assets = os.path.join(TEMPLATE_DIR, "assets")
    for fname in ["cover_bg.png", "cta_bg.png"]:
        src = os.path.join(template_assets, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(assets_dir, fname))
            print(f"  ✓ 템플릿 에셋 복사: {fname}")

    for idx, card in enumerate(data["cards"], start=2):
        num = str(idx).zfill(2)
        theme = card["theme"]
        img_file = f"card_{num}_{theme}.png"
        img_path = os.path.join(assets_dir, img_file)

        if os.path.exists(img_path):
            if reuse_assets:
                print(f"  [{num}] 기존 로컬 이미지를 재사용합니다: {img_file}")
                continue
            os.remove(img_path)
            print(f"  [{num}] 기존 로컬 이미지를 삭제하고 다시 받습니다: {img_file}")

        image_url = card.get("image_url")
        if image_url:
            print(f"  [{num}] 기사 이미지 URL 다운로드 시도 중... ({image_url})")
            if download_and_resize(image_url, img_path):
                print(f"  ✓ [{num}] 기사 이미지 URL 다운로드 성공")
                continue
            print(f"  ✗ [{num}] 기사 이미지 URL 다운로드 실패")
            missing_images.append(img_file)
            continue

        if not allow_wikimedia_fallback:
            # [수정] 하드 중단 대신 트리거 로그 출력 후 missing_images에 추가
            # AI가 이미지를 생성한 뒤 image_url을 채워주면 다음 빌드에서 정상 처리됨
            print(f"[MISSING_IMAGE_TRIGGER] card_num={num}, theme={theme}, company={card['company']}, title={card['title']}, reason=no_image_url")
            missing_images.append(img_file)
            continue

        query = card.get("image_search", card["company"])
        print(f"  [{num}] '{query}' Wikimedia 검색 중...")
        filename = search_wikimedia(query)
        if filename:
            url = wikimedia_url(filename)
            print(f"    → {filename}")
            if not download_and_resize(url, img_path):
                missing_images.append(img_file)
        else:
            print("    ✗ 검색 결과 없음")
            missing_images.append(img_file)

    if missing_images:
        # [수정] 이미지 누락 시 하드 중단(sys.exit) 대신 경고 출력 후 계속 진행
        # 누락된 카드는 AI가 이미지를 생성해 image_url을 채운 뒤 --reuse-assets로 재빌드
        print(f"  ⚠ 이미지 누락 카드 {len(missing_images)}개: {', '.join(missing_images)}")
        print("  ⚠ [MISSING_IMAGE_TRIGGER]가 발생한 카드는 AI 이미지 생성 후 --reuse-assets로 재빌드하세요.")
        return False
    return True


def export_pngs(data, output_dir):
    date = data["date"]
    shutil.copy2(os.path.join(TEMPLATE_DIR, "export_cards.js"), os.path.join(output_dir, "export_cards.js"))

    print("  Playwright 렌더링 시작...")
    result = subprocess.run(
        ["node", "export_cards.js", "--html", "index.html", "--out", "output", "--date", date, "--prefix", "card"],
        cwd=output_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ✗ 렌더링 실패: {result.stderr}")
        return False
    print(f"  ✓ {result.stdout.strip()}")

    out_png_dir = os.path.join(output_dir, "output")
    files = sorted(f for f in os.listdir(out_png_dir) if f.startswith(f"{date}_card_") and f.endswith(".png"))
    if not files:
        print("  ✗ PNG 파일 없음")
        return False

    images = [Image.open(os.path.join(out_png_dir, f)) for f in files]
    w, h = images[0].size
    cols = 4
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (w * cols, h * rows), (255, 255, 255))
    for idx, img in enumerate(images):
        sheet.paste(img, ((idx % cols) * w, (idx // cols) * h))
    sheet.save(os.path.join(out_png_dir, "contact_sheet.png"))
    print(f"  ✓ 콘택트 시트 저장 ({len(files)}장 → {cols}x{rows} 격자)")
    return True


def generate_report(data, output_dir):
    date = data["date"]
    out_png_dir = os.path.join(output_dir, "output")
    files = sorted(f for f in os.listdir(out_png_dir) if f.startswith(f"{date}_card_") and f.endswith(".png"))
    report = {"date": date, "card_count": len(files), "news_count": len(data["cards"]), "files": []}
    for fname in files:
        path = os.path.join(out_png_dir, fname)
        report["files"].append({"filename": fname, "size_bytes": os.stat(path).st_size})
    with open(os.path.join(out_png_dir, "export_report.json"), "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    print("  ✓ export_report.json 생성")


def copy_to_downloads(data, output_dir):
    date = data["date"]
    out_png_dir = os.path.join(output_dir, "output")
    dl_dir = os.path.join(DOWNLOADS_DIR, f"{date}_daily_news")
    os.makedirs(dl_dir, exist_ok=True)
    count = 0
    for fname in sorted(os.listdir(out_png_dir)):
        if fname.endswith(".png"):
            shutil.copy2(os.path.join(out_png_dir, fname), os.path.join(dl_dir, fname))
            count += 1
    print(f"  ✓ {count}개 파일 → {dl_dir}")


def main():
    parser = argparse.ArgumentParser(description="Daily News Card Builder")
    parser.add_argument("--data", required=True, help="news_data.json 경로")
    parser.add_argument("--publish", action="store_true", help="빌드 후 Instagram/Threads/Telegram 자동 게시")
    parser.add_argument("--reuse-assets", action="store_true", help="기존 assets/card_*.png를 재사용합니다. 기본값은 재다운로드입니다.")
    parser.add_argument("--allow-wikimedia-fallback", action="store_true", help="image_url이 없을 때 Wikimedia 자동 검색을 허용합니다.")
    parser.add_argument("--allow-korean-threads", action="store_true", help="Threads 문구에 한국어가 포함되어도 허용합니다.")
    parser.add_argument("--clean-after-publish", action="store_true", help="--publish 후 publish.py --clean까지 실행합니다.")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    validate_news_data(
        data,
        allow_korean_threads=args.allow_korean_threads,
        allow_wikimedia_fallback=args.allow_wikimedia_fallback,
    )

    date = data["date"]
    output_dir = os.path.join(SCRIPT_DIR, date)
    os.makedirs(output_dir, exist_ok=True)
    shutil.copy2(args.data, os.path.join(output_dir, "news_data.json"))

    print(f"\n{'='*60}")
    print(f"  Daily News Card Builder — {date}")
    print(f"{'='*60}")

    print("\n[1/6] HTML 생성")
    generate_html(data, output_dir)

    print("\n[2/6] CSS 생성")
    generate_css(data, output_dir)

    print("\n[3/6] 이미지 확보")
    images_ok = download_images(data, output_dir, reuse_assets=args.reuse_assets, allow_wikimedia_fallback=args.allow_wikimedia_fallback)
    if not images_ok:
        print("\n  ⚠ 일부 이미지가 누락되어 빌드를 중단합니다.")
        print("  ⚠ AI로 누락 이미지를 생성한 뒤 news_data.json의 image_url을 채우고 --reuse-assets로 재실행하세요.")
        sys.exit(1)

    print("\n[4/6] PNG 렌더링")
    if not export_pngs(data, output_dir):
        sys.exit(1)

    print("\n[5/6] 빌드 리포트")
    generate_report(data, output_dir)

    print("\n[6/6] Downloads 복사")
    copy_to_downloads(data, output_dir)

    print(f"\n{'='*60}")
    print(f"  ✅ 빌드 완료: {output_dir}")
    print(f"  📁 다운로드: ~/Downloads/{date}_daily_news/")
    print(f"{'='*60}\n")

    if args.publish:
        publish_script = os.path.join(SCRIPT_DIR, "publish.py")
        publish_cmd = [
            sys.executable,
            publish_script,
            "--date",
            date,
            "--data",
            os.path.join(output_dir, "news_data.json"),
        ]
        if args.clean_after_publish:
            publish_cmd.append("--clean")
        print(f"\n{'='*60}")
        print("  📡 자동 게시 시작...")
        print(f"{'='*60}")
        subprocess.run(publish_cmd, cwd=SCRIPT_DIR)


if __name__ == "__main__":
    main()

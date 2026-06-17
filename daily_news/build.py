#!/usr/bin/env python3
"""
Daily IT & AI News Card News Builder
=====================================
고정 템플릿 기반으로 news_data.json을 검증한 뒤 카드뉴스를 생성합니다.

기본 정책은 fail-fast입니다. 출처/이미지가 불확실하면 그럴듯한 카드뉴스를
만들지 않고 빌드를 중단합니다.

Usage:
  python3 build.py --data news_data.json
  python3 build.py --data news_data.json --refresh-assets
"""

import argparse
import html
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, ImageStat

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR / "template"
DOWNLOADS_DIR = Path.home() / "Downloads"
KST = datetime.now().astimezone().tzinfo

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$")
HANGUL_RE = re.compile(r"[가-힣]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BROAD_SECTION_WORDS = {
    "", "news", "business", "tech", "technology", "ai", "artificial-intelligence",
    "world", "markets", "finance", "innovation", "policy", "science", "latest",
    "category", "topics", "tag", "companies", "enterprise", "semiconductors",
}


def fail(message):
    raise ValueError(f"\n[유효성 검증 에러] {message}")


def warn(message):
    print(f"  ⚠ {message}")


def is_specific_article_url(url):
    """홈/섹션 URL이 아니라 개별 기사 URL에 가까운지 보수적으로 판정합니다."""
    try:
        p = urlparse(url)
    except Exception:
        return False

    if p.scheme not in {"http", "https"} or not p.netloc:
        return False

    segments = [s for s in p.path.strip("/").split("/") if s]
    if not segments:
        return False

    lowered = [s.lower() for s in segments]
    if len(lowered) == 1 and lowered[0] in BROAD_SECTION_WORDS:
        return False
    if len(lowered) <= 2 and all(s in BROAD_SECTION_WORDS for s in lowered):
        return False

    joined = "/".join(lowered)
    has_article_signal = (
        bool(re.search(r"\d{4}|\d{6,}|[a-f0-9]{12,}", joined))
        or joined.endswith((".html", ".htm"))
        or len(segments) >= 3
        or bool(p.query)
    )
    return has_article_signal


def contains_hangul(value):
    return bool(HANGUL_RE.search(str(value)))


def validate_text_lengths(card, index):
    title = str(card.get("title", ""))
    body = str(card.get("body", ""))
    if len(title) > 95:
        fail(f"{index}번 카드 제목이 너무 깁니다. 95자 이하 권장: {len(title)}자")
    if len(body) > 360:
        fail(f"{index}번 카드 본문이 너무 깁니다. 360자 이하 권장: {len(body)}자")

    threads = card.get("threads", {})
    if isinstance(threads, dict):
        composed = " ".join(str(threads.get(k, "")) for k in ["hook", "detail", "context"])
        if len(composed) > 500:
            fail(f"{index}번 카드 Threads 본문이 500자를 초과합니다: {len(composed)}자")
        for option in threads.get("poll_options", []) or []:
            if len(str(option)) > 25:
                fail(f"{index}번 카드 투표 선택지가 너무 깁니다: {option}")


def validate_news_data(data, args):
    """뉴스 원고·출처·이미지 안전성을 fail-fast로 검증합니다."""
    if not isinstance(data, dict):
        fail("news_data.json 최상위 값은 객체여야 합니다.")

    date = data.get("date")
    if not isinstance(date, str) or not DATE_RE.match(date):
        fail("date는 YYYY-MM-DD 형식이어야 합니다.")

    try:
        data_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        fail(f"date 값이 실제 날짜가 아닙니다: {date}")

    today = datetime.now(KST).date()
    if not args.allow_date_mismatch:
        if data_date > today:
            fail(f"미래 날짜 데이터입니다. data.date={date}, today={today.isoformat()}")
        if data_date < today - timedelta(days=2):
            fail(
                f"너무 오래된 날짜 데이터입니다. data.date={date}, today={today.isoformat()} "
                "과거 자료를 재빌드하려면 --allow-date-mismatch를 사용하십시오."
            )

    cards = data.get("cards")
    if not isinstance(cards, list) or not cards:
        fail("cards는 비어 있지 않은 배열이어야 합니다.")
    if len(cards) > 8:
        fail(f"뉴스 카드가 너무 많습니다. 최대 8개 권장, 현재 {len(cards)}개")

    for idx, card in enumerate(cards, start=1):
        if not isinstance(card, dict):
            fail(f"{idx}번 card는 객체여야 합니다.")

        required = ["theme", "company", "status", "title", "body", "source", "colors"]
        missing = [k for k in required if not card.get(k)]
        if missing:
            fail(f"{idx}번 카드 필수 필드 누락: {', '.join(missing)}")

        if card.get("status") not in {"official", "reported"}:
            fail(f"{idx}번 카드 status는 official/reported 중 하나여야 합니다: {card.get('status')}")

        colors = card.get("colors", {})
        for name in ["bg", "soft", "ink"]:
            if not HEX_COLOR_RE.match(str(colors.get(name, ""))):
                fail(f"{idx}번 카드 colors.{name}가 안전한 hex 색상이 아닙니다: {colors.get(name)}")

        validate_text_lengths(card, idx)

        if not args.allow_korean_threads:
            threads = card.get("threads", {})
            if isinstance(threads, dict):
                fields = ["hook", "detail", "context", "question"]
                values = [threads.get(k, "") for k in fields]
                values += list(threads.get("poll_options", []) or [])
                if any(contains_hangul(v) for v in values):
                    fail(
                        f"{idx}번 카드 Threads 문구에 한글이 포함되어 있습니다. "
                        "영문 운영이면 영어로 바꾸거나, 한국어 운영이면 --allow-korean-threads를 사용하십시오."
                    )

        urls = []
        if card.get("source_url"):
            urls.append(card["source_url"])
        urls.extend(card.get("related_urls", []) or [])
        if not urls:
            fail(f"{idx}번 카드에 source_url 또는 related_urls가 없습니다.")

        for url in urls:
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                fail(f"{idx}번 카드 URL 형식 오류: {url}")
            if not args.allow_broad_urls and not is_specific_article_url(url):
                fail(
                    f"{idx}번 카드 URL이 개별 기사 URL이 아니라 홈/섹션 URL로 보입니다: {url}\n"
                    "  해결: bbc.com/news/business, cnbc.com 같은 도메인/섹션 대신 실제 기사 상세 URL을 넣으십시오."
                )

        source = str(card.get("source", ""))
        if len(source.split(",")) < 1 or any(len(part.strip()) < 2 for part in source.split(",")):
            fail(f"{idx}번 카드 source 표기가 부실합니다: {source}")

    print(f"  ✓ news_data.json 검증 완료 ({len(cards)}개 뉴스)")


def generate_html(data, output_dir):
    date = data["date"]
    date_display = date.replace("-", ".")
    cards = data["cards"]
    n = len(cards)

    mode = data.get("mode", "daily")
    if mode == "event":
        cover_eyebrow = "Special Event Briefing"
        cover_title = data.get("event_title", "스페셜 이벤트")
    else:
        cover_eyebrow = "Daily IT &amp; AI Briefing"
        cover_title = "오늘의 IT 뉴스 브리핑"

    cover_title_safe = html.escape(str(cover_title))
    date_safe = html.escape(date)
    date_display_safe = html.escape(date_display)

    html_doc = f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{date_safe} {cover_title_safe}</title>
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <main class="deck" aria-label="{date_display_safe} {cover_title_safe} 카드뉴스">
    <section class="card card--thumbnail" id="card-01" data-card-number="01">
      <div class="cover-art" aria-hidden="true"></div>
      <div class="card-inner">
        <header class="topline">
          <span class="card-number">01</span>
          <span class="date">{date_display_safe}</span>
        </header>
        <div class="hero-copy">
          <p class="eyebrow">{cover_eyebrow}</p>
          <h1>{cover_title_safe}</h1>
          <p class="subtitle">확인된 글로벌 IT/AI 핵심 소식 {n}개</p>
        </div>
        <div class="tag-row" aria-label="태그">
          <span>{n} NEWS</span>
          <span>FACT CHECK</span>
          <span>TECH TREND</span>
        </div>
        <p class="source-line">출처: 각 카드 하단 표기</p>
      </div>
    </section>
'''

    for i, card in enumerate(cards):
        num = str(i + 2).zfill(2)
        status_class = "status--official" if card["status"] == "official" else "status--reported"
        status_text = "공식 확인" if card["status"] == "official" else "보도 기준"
        theme = html.escape(str(card["theme"]))
        company = html.escape(str(card["company"]))
        title = html.escape(str(card["title"]))
        body = html.escape(str(card["body"]))
        source = html.escape(str(card["source"]))

        html_doc += f'''
    <section class="card card--brief theme-{theme}" id="card-{num}" data-card-number="{num}">
      <div class="visual-area" aria-hidden="true">
        <span class="image-badge">{company} · {status_text}</span>
      </div>
      <div class="text-panel">
        <header class="brief-header">
          <span class="company">{company}</span>
          <span class="status {status_class}">{status_text}</span>
        </header>
        <h2>{title}</h2>
        <p>{body}</p>
        <footer class="card-footer">{source}</footer>
      </div>
    </section>
'''

    cta_num = str(n + 2).zfill(2)
    sources = html.escape(", ".join(str(c["company"]) for c in cards))
    html_doc += f'''
    <section class="card card--cta" id="card-{cta_num}" data-card-number="{cta_num}">
      <div class="cta-art" aria-hidden="true"></div>
      <div class="card-inner">
        <header class="topline">
          <span class="card-number">{cta_num}</span>
          <span class="date">{date_display_safe}</span>
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
        <footer class="card-footer card-footer--cta">출처: {sources} 공식 발표 및 주요 외신 보도 기준</footer>
      </div>
    </section>
  </main>
</body>
</html>
'''

    path = output_dir / "index.html"
    path.write_text(html_doc, encoding="utf-8")
    print(f"  ✓ index.html 생성 ({n}개 뉴스 카드)")


def generate_css(data, output_dir):
    base_path = TEMPLATE_DIR / "style.css"
    base_css = base_path.read_text(encoding="utf-8")

    themes = "\n/* Themes - Auto-generated */\n"
    for i, card in enumerate(data["cards"]):
        num = str(i + 2).zfill(2)
        theme = str(card["theme"])
        c = card["colors"]
        img = f"card_{num}_{theme}.png"
        themes += f"""#card-{num} {{
  --theme-bg: {c['bg']};
  --theme-soft: {c['soft']};
  --theme-ink: {c['ink']};
  --image-bg: url(\"./assets/{img}\") center / cover no-repeat;
}}

"""

    (output_dir / "style.css").write_text(base_css + themes, encoding="utf-8")
    print("  ✓ style.css 생성 (베이스 + 테마)")


def looks_like_logo_or_text_image(img):
    sample = img.convert("RGB").resize((180, 117))
    stat = ImageStat.Stat(sample)
    avg_stddev = sum(stat.stddev) / 3
    quantized = sample.quantize(colors=64)
    colors = quantized.getcolors(180 * 117) or []
    if not colors:
        return False
    total = 180 * 117
    color_count = len(colors)
    top_ratio = max(count for count, _ in colors) / total
    return (
        color_count <= 16 and top_ratio >= 0.30
        or color_count <= 32 and top_ratio >= 0.45 and avg_stddev < 42
        or color_count <= 48 and top_ratio >= 0.58
        or avg_stddev < 12
    )


def crop_and_save_image(src_path, out_path, w=1080, h=702):
    with Image.open(src_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")
        ow, oh = img.size
        if ow < 500 or oh < 320:
            raise ValueError(f"이미지 해상도가 너무 낮습니다: {ow}x{oh}")
        if ow < oh:
            raise ValueError(f"세로형 이미지는 카드 배경으로 사용하지 않습니다: {ow}x{oh}")
        if ow / oh > 2.6:
            raise ValueError(f"배너형 이미지는 카드 배경으로 사용하지 않습니다: {ow}x{oh}")
        if looks_like_logo_or_text_image(img):
            raise ValueError("로고/텍스트 중심 이미지로 판단되어 기각합니다.")

        target_ratio = w / h
        current_ratio = ow / oh
        if current_ratio > target_ratio:
            nw = int(oh * target_ratio)
            left = (ow - nw) // 2
            img = img.crop((left, 0, left + nw, oh))
        else:
            nh = int(ow / target_ratio)
            top = (oh - nh) // 2
            img = img.crop((0, top, ow, top + nh))
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        img.save(out_path, "PNG")


def download_and_resize(url, out_path):
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        if res.status_code != 200:
            print(f"    ✗ HTTP {res.status_code}")
            return False
        tmp.write_bytes(res.content)
        crop_and_save_image(tmp, out_path)
        print("    ✓ 저장 완료 (1080x702)")
        return True
    except Exception as e:
        print(f"    ✗ 이미지 검증/저장 실패: {e}")
        return False
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def download_images(data, output_dir, args):
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    missing_images = []

    tmpl_assets = TEMPLATE_DIR / "assets"
    for fname in ["cover_bg.png", "cta_bg.png"]:
        src = tmpl_assets / fname
        dst = assets_dir / fname
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ 템플릿 에셋 복사: {fname}")

    for i, card in enumerate(data["cards"]):
        num = str(i + 2).zfill(2)
        theme = str(card["theme"])
        img_file = f"card_{num}_{theme}.png"
        img_path = assets_dir / img_file

        if args.refresh_assets and img_path.exists():
            img_path.unlink()
            print(f"  [{num}] 기존 이미지 삭제 후 새로 검증합니다: {img_file}")

        if img_path.exists():
            print(f"  [{num}] 로컬 이미지 사용: {img_file}")
            continue

        img_url = card.get("image_url")
        if img_url:
            print(f"  [{num}] 기사 이미지 URL 다운로드 시도 중... ({img_url})")
            if download_and_resize(img_url, img_path):
                print(f"  ✓ [{num}] 기사 이미지 URL 다운로드 성공")
                continue
            warn(f"{num}번 image_url 다운로드 실패. 수동 교체 또는 fuse_news.py 재실행 필요")

        if args.allow_wikimedia_fallback:
            warn(f"{num}번 카드가 Wikimedia 폴백을 허용했습니다. 시각적 오매칭 가능성이 있습니다.")

        print(
            f"[MISSING_IMAGE_TRIGGER] card_num={num}, theme={theme}, "
            f"company={card.get('company')}, title={card.get('title')}, query={card.get('image_search')}"
        )
        missing_images.append(img_file)

    if missing_images:
        print(f"  ✗ 이미지 누락으로 빌드를 중단합니다: {', '.join(missing_images)}")
        print("  해결: fuse_news.py로 기사 이미지를 먼저 확보하거나, 각 카드에 검증된 image_url을 넣으십시오.")
        return False
    return True


def export_pngs(data, output_dir):
    date = data["date"]
    shutil.copy2(TEMPLATE_DIR / "export_cards.js", output_dir / "export_cards.js")

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

    print("  콘택트 시트 생성 중...")
    out_png_dir = output_dir / "output"
    files = sorted(f for f in out_png_dir.iterdir() if f.name.startswith(f"{date}_card_") and f.suffix == ".png")
    if not files:
        print("  ✗ PNG 파일 없음")
        return False

    images = [Image.open(f) for f in files]
    try:
        w, h = images[0].size
        cols = 4
        rows = math.ceil(len(images) / cols)
        sheet = Image.new("RGB", (w * cols, h * rows), (255, 255, 255))
        for idx, img in enumerate(images):
            sheet.paste(img, ((idx % cols) * w, (idx // cols) * h))
        sheet.save(out_png_dir / "contact_sheet.png")
        print(f"  ✓ 콘택트 시트 저장 ({len(files)}장 → {cols}x{rows} 격자)")
    finally:
        for img in images:
            img.close()
    return True


def copy_to_downloads(data, output_dir):
    date = data["date"]
    dl_dir = DOWNLOADS_DIR / f"{date}_daily_news"
    dl_dir.mkdir(parents=True, exist_ok=True)

    out_png_dir = output_dir / "output"
    count = 0
    for f in sorted(out_png_dir.iterdir()):
        if f.suffix == ".png":
            shutil.copy2(f, dl_dir / f.name)
            count += 1
    print(f"  ✓ {count}개 파일 → {dl_dir}")


def generate_report(data, output_dir):
    date = data["date"]
    out_png_dir = output_dir / "output"
    files = sorted(f for f in out_png_dir.iterdir() if f.name.startswith(f"{date}_card_") and f.suffix == ".png")
    report = {
        "date": date,
        "card_count": len(files),
        "news_count": len(data["cards"]),
        "files": [{"filename": f.name, "size_bytes": f.stat().st_size} for f in files],
    }
    (out_png_dir / "export_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  ✓ export_report.json 생성")


def main():
    parser = argparse.ArgumentParser(description="Daily News Card Builder")
    parser.add_argument("--data", required=True, help="news_data.json 경로")
    parser.add_argument("--publish", action="store_true", help="빌드 후 Instagram/Threads/Telegram 자동 게시")
    parser.add_argument("--refresh-assets", action="store_true", help="기존 카드 이미지를 삭제하고 다시 검증/다운로드")
    parser.add_argument("--clean-after-publish", action="store_true", help="publish.py에 --clean 전달")
    parser.add_argument("--allow-date-mismatch", action="store_true", help="과거/미래 날짜 데이터 빌드 허용")
    parser.add_argument("--allow-broad-urls", action="store_true", help="홈/섹션 URL 허용. 운영 게시 전에는 권장하지 않음")
    parser.add_argument("--allow-korean-threads", action="store_true", help="Threads 문구의 한글 허용")
    parser.add_argument("--allow-wikimedia-fallback", action="store_true", help="안전하지 않은 이미지 폴백 허용 플래그. 현재는 경고만 표시")
    args = parser.parse_args()

    data_path = Path(args.data)
    data = json.loads(data_path.read_text(encoding="utf-8"))

    validate_news_data(data, args)

    date = data["date"]
    output_dir = SCRIPT_DIR / date
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(data_path, output_dir / "news_data.json")

    print(f"\n{'=' * 60}")
    print(f"  Daily News Card Builder — {date}")
    print(f"{'=' * 60}")

    print("\n[1/6] HTML 생성")
    generate_html(data, output_dir)

    print("\n[2/6] CSS 생성")
    generate_css(data, output_dir)

    print("\n[3/6] 이미지 확보")
    if not download_images(data, output_dir, args):
        sys.exit(1)

    print("\n[4/6] PNG 렌더링")
    if not export_pngs(data, output_dir):
        sys.exit(1)

    print("\n[5/6] 빌드 리포트")
    generate_report(data, output_dir)

    print("\n[6/6] Downloads 복사")
    copy_to_downloads(data, output_dir)

    print(f"\n{'=' * 60}")
    print(f"  ✅ 빌드 완료: {output_dir}")
    print(f"  📁 다운로드: ~/Downloads/{date}_daily_news/")
    print(f"{'=' * 60}\n")

    if args.publish:
        publish_script = SCRIPT_DIR / "publish.py"
        cmd = [sys.executable, str(publish_script), "--date", date, "--data", str(output_dir / "news_data.json")]
        if args.clean_after_publish:
            cmd.append("--clean")
        print(f"\n{'=' * 60}")
        print("  📡 자동 게시 시작...")
        print(f"{'=' * 60}")
        subprocess.run(cmd, cwd=SCRIPT_DIR, check=False)


if __name__ == "__main__":
    main()

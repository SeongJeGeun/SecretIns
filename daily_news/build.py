#!/usr/bin/env python3
"""
Daily IT & AI News Card News Builder
=====================================
고정 템플릿 기반으로 news_data.json만 넣으면 카드뉴스를 자동 생성합니다.

Usage:
  python3 build.py --data news_data.json
"""

import os
import sys
import json
import shutil
import hashlib
import subprocess
import argparse
import math

try:
    import requests
except ImportError:
    print("requests 패키지 설치 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from PIL import Image
except ImportError:
    print("Pillow 패키지 설치 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "template")
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")

# ─────────────────────────────────────────────
# 1. HTML 생성
# ─────────────────────────────────────────────
def generate_html(data, output_dir):
    date = data["date"]
    date_display = date.replace("-", ".")
    cards = data["cards"]
    n = len(cards)

    mode = data.get("mode", "daily")
    if mode == "event":
        event_title = data.get("event_title", "스페셜 이벤트")
        cover_eyebrow = "Special Event Briefing"
        cover_title = event_title
    else:
        cover_eyebrow = "Daily IT &amp; AI Briefing"
        cover_title = "오늘의 IT 뉴스 브리핑"

    # Cover
    html = f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{date} {cover_title}</title>
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <main class="deck" aria-label="{date_display} {cover_title} 카드뉴스">
    <section class="card card--thumbnail" id="card-01" data-card-number="01">
      <div class="cover-art" aria-hidden="true"></div>
      <div class="card-inner">
        <header class="topline">
          <span class="card-number">01</span>
          <span class="date">{date_display}</span>
        </header>
        <div class="hero-copy">
          <p class="eyebrow">{cover_eyebrow}</p>
          <h1>{cover_title}</h1>
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

    # News cards
    for i, card in enumerate(cards):
        num = str(i + 2).zfill(2)
        status_class = "status--official" if card["status"] == "official" else "status--reported"
        status_text = "공식 확인" if card["status"] == "official" else "보도 기준"

        html += f'''
    <section class="card card--brief theme-{card["theme"]}" id="card-{num}" data-card-number="{num}">
      <div class="visual-area" aria-hidden="true">
        <span class="image-badge">{card["company"]} · {status_text}</span>
      </div>
      <div class="text-panel">
        <header class="brief-header">
          <span class="company">{card["company"]}</span>
          <span class="status {status_class}">{status_text}</span>
        </header>
        <h2>{card["title"]}</h2>
        <p>{card["body"]}</p>
        <footer class="card-footer">{card["source"]}</footer>
      </div>
    </section>
'''

    # CTA
    cta_num = str(n + 2).zfill(2)
    sources = ", ".join([c["company"] for c in cards])

    html += f'''
    <section class="card card--cta" id="card-{cta_num}" data-card-number="{cta_num}">
      <div class="cta-art" aria-hidden="true"></div>
      <div class="card-inner">
        <header class="topline">
          <span class="card-number">{cta_num}</span>
          <span class="date">{date_display}</span>
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

    path = os.path.join(output_dir, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ index.html 생성 ({n}개 뉴스 카드)")


# ─────────────────────────────────────────────
# 2. CSS 생성 (베이스 복사 + 테마 주입)
# ─────────────────────────────────────────────
def generate_css(data, output_dir):
    base_path = os.path.join(TEMPLATE_DIR, "style.css")
    with open(base_path, "r", encoding="utf-8") as f:
        base_css = f.read()

    themes = "\n/* Themes - Auto-generated */\n"
    for i, card in enumerate(data["cards"]):
        num = str(i + 2).zfill(2)
        t = card["theme"]
        c = card["colors"]
        img = f"card_{num}_{t}.png"
        themes += f""".theme-{t} {{
  --theme-bg: {c["bg"]};
  --theme-soft: {c["soft"]};
  --theme-ink: {c["ink"]};
  --image-bg: url("./assets/{img}") center / cover no-repeat;
}}

"""

    path = os.path.join(output_dir, "style.css")
    with open(path, "w", encoding="utf-8") as f:
        f.write(base_css + themes)
    print("  ✓ style.css 생성 (베이스 + 테마)")


# ─────────────────────────────────────────────
# 3. 이미지 다운로드 및 리사이즈
# ─────────────────────────────────────────────
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def search_wikimedia(query):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "format": "json",
        "list": "search", "srsearch": query + " filetype:bitmap",
        "srnamespace": 6, "srlimit": 5
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            results = r.json().get("query", {}).get("search", [])
            if results:
                return results[0]["title"].replace("File:", "")
    except Exception:
        pass
    return None


def wikimedia_url(filename):
    name = filename.replace(" ", "_")
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{name}"


def download_and_resize(url, out_path, w=1080, h=702):
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        if res.status_code != 200:
            print(f"    ✗ HTTP {res.status_code}")
            return False

        tmp = out_path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(res.content)

        with Image.open(tmp) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            ow, oh = img.size
            tr = w / h
            cr = ow / oh
            if cr > tr:
                nw = int(oh * tr)
                left = (ow - nw) // 2
                img = img.crop((left, 0, left + nw, oh))
            else:
                nh = int(ow / tr)
                top = (oh - nh) // 2
                img = img.crop((0, top, ow, top + nh))
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            img.save(out_path, "PNG")

        os.remove(tmp)
        print(f"    ✓ 저장 완료 ({w}x{h})")
        return True
    except Exception as e:
        print(f"    ✗ 에러: {e}")
        return False


def generate_placeholder(out_path, color, w=1080, h=702):
    """이미지를 찾지 못했을 때 단색 플레이스홀더 생성"""
    img = Image.new("RGB", (w, h), color)
    img.save(out_path, "PNG")
    print(f"    ⚠ 플레이스홀더 생성 ({color})")


def download_images(data, output_dir):
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 템플릿 고정 에셋 복사 (커버, CTA)
    tmpl_assets = os.path.join(TEMPLATE_DIR, "assets")
    for fname in ["cover_bg.png", "cta_bg.png"]:
        src = os.path.join(tmpl_assets, fname)
        dst = os.path.join(assets_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  ✓ 템플릿 에셋 복사: {fname}")

    # 뉴스 이미지 다운로드
    for i, card in enumerate(data["cards"]):
        num = str(i + 2).zfill(2)
        theme = card["theme"]
        img_file = f"card_{num}_{theme}.png"
        img_path = os.path.join(assets_dir, img_file)

        # 만약 로컬에 이미지가 이미 준비되어 있다면 다운로드 건너뜀
        if os.path.exists(img_path):
            print(f"  [{num}] 로컬 이미지가 이미 존재하여 다운로드를 건너뜁니다: {img_file}")
            continue

        # 1순위: 기사 내 직접 제공된 이미지 URL (image_url) 다운로드 시도
        img_url = card.get("image_url")
        if img_url:
            print(f"  [{num}] 기사 이미지 URL 다운로드 시도 중... ({img_url})")
            ok = download_and_resize(img_url, img_path)
            if ok:
                print(f"  ✓ [{num}] 기사 이미지 URL 다운로드 성공!")
                continue
            else:
                print(f"  ✗ [{num}] 기사 이미지 URL 다운로드 실패. Wikimedia 검색으로 폴백합니다.")

        # 2순위: Wikimedia 검색 수행
        query = card.get("image_search", card["company"])
        print(f"  [{num}] '{query}' Wikimedia 검색 중...")

        filename = search_wikimedia(query)
        if filename:
            url = wikimedia_url(filename)
            print(f"    → {filename}")
            ok = download_and_resize(url, img_path)
            if not ok:
                generate_placeholder(img_path, card["colors"]["bg"])
        else:
            print(f"    ✗ 검색 결과 없음")
            generate_placeholder(img_path, card["colors"]["bg"])


# ─────────────────────────────────────────────
# 4. PNG 추출 (Playwright) + 콘택트 시트
# ─────────────────────────────────────────────
def export_pngs(data, output_dir):
    date = data["date"]

    # export_cards.js 복사
    src_js = os.path.join(TEMPLATE_DIR, "export_cards.js")
    dst_js = os.path.join(output_dir, "export_cards.js")
    shutil.copy2(src_js, dst_js)

    # Playwright 실행
    print("  Playwright 렌더링 시작...")
    result = subprocess.run(
        ["node", "export_cards.js", "--html", "index.html",
         "--out", "output", "--date", date, "--prefix", "card"],
        cwd=output_dir, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ✗ 렌더링 실패: {result.stderr}")
        return False
    print(f"  ✓ {result.stdout.strip()}")

    # 콘택트 시트 생성
    print("  콘택트 시트 생성 중...")
    out_png_dir = os.path.join(output_dir, "output")
    files = sorted([
        f for f in os.listdir(out_png_dir)
        if f.startswith(f"{date}_card_") and f.endswith(".png")
    ])
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
    sheet_path = os.path.join(out_png_dir, "contact_sheet.png")
    sheet.save(sheet_path)
    print(f"  ✓ 콘택트 시트 저장 ({len(files)}장 → {cols}x{rows} 격자)")

    return True


# ─────────────────────────────────────────────
# 5. Downloads 폴더로 복사
# ─────────────────────────────────────────────
def copy_to_downloads(data, output_dir):
    date = data["date"]
    dl_dir = os.path.join(DOWNLOADS_DIR, f"{date}_daily_news")
    os.makedirs(dl_dir, exist_ok=True)

    out_png_dir = os.path.join(output_dir, "output")
    count = 0
    for f in sorted(os.listdir(out_png_dir)):
        if f.endswith(".png"):
            shutil.copy2(os.path.join(out_png_dir, f), os.path.join(dl_dir, f))
            count += 1

    print(f"  ✓ {count}개 파일 → {dl_dir}")


# ─────────────────────────────────────────────
# 6. 빌드 리포트 생성
# ─────────────────────────────────────────────
def generate_report(data, output_dir):
    date = data["date"]
    out_png_dir = os.path.join(output_dir, "output")
    files = sorted([
        f for f in os.listdir(out_png_dir)
        if f.startswith(f"{date}_card_") and f.endswith(".png")
    ])

    report = {
        "date": date,
        "card_count": len(files),
        "news_count": len(data["cards"]),
        "files": []
    }
    for f in files:
        fpath = os.path.join(out_png_dir, f)
        stat = os.stat(fpath)
        report["files"].append({
            "filename": f,
            "size_bytes": stat.st_size
        })

    report_path = os.path.join(out_png_dir, "export_report.json")
    with open(report_path, "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    print(f"  ✓ export_report.json 생성")


def validate_news_data(data):
    """뉴스 데이터의 논리적 정합성 및 팩트 체크 검증"""
    from datetime import datetime
    
    # 주요 이벤트의 실제 공식 발표 시간 (한국 시간 KST 기준)
    EVENT_RELEASE_TIMES = {
        "wwdc": datetime(2026, 6, 9, 2, 0, 0),  # WWDC 2026 기조연설 시작 시간
    }
    
    mode = data.get("mode", "daily")
    event_title = data.get("event_title", "")
    cards = data.get("cards", [])
    current_time = datetime.now()
    
    for event_key, release_time in EVENT_RELEASE_TIMES.items():
        match = False
        if event_key in event_title.lower():
            match = True
        else:
            for c in cards:
                if (event_key in c.get("title", "").lower() or 
                    event_key in c.get("body", "").lower() or 
                    event_key in c.get("image_search", "").lower()):
                    match = True
                    break
        
        if match:
            if current_time < release_time:
                official_cards = [c for c in cards if c.get("status") == "official"]
                if official_cards:
                    titles = [f"'{c.get('title')}'" for c in official_cards]
                    err_msg = (
                        f"\n[유효성 검증 에러] 아직 공식 발표 전인 이벤트 뉴스가 'official'로 표기되었습니다.\n"
                        f"  - 대상 이벤트: {event_key.upper()}\n"
                        f"  - 발표 예정 시간: {release_time.strftime('%Y-%m-%d %H:%M:%S')} KST\n"
                        f"  - 현재 시스템 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')} KST\n"
                        f"  - 오류 카드: {', '.join(titles)}\n\n"
                        f"해결 방법: 카드의 'status'를 'reported'로 변경하거나, 실제 발표 시간 이후에 빌드하십시오."
                    )
                    raise ValueError(err_msg)

    # 2. 관련 검증 URL (related_urls) 형식 검증
    for idx, c in enumerate(cards):
        comp = c.get("company", f"Card {idx+1}")
        urls = c.get("related_urls", [])
        if not isinstance(urls, list):
            raise ValueError(f"\n[유효성 검증 에러] {comp} 카드의 'related_urls' 필드는 배열(List) 형식이어야 합니다.")
        for url in urls:
            if not (url.startswith("http://") or url.startswith("https://")):
                raise ValueError(f"\n[유효성 검증 에러] {comp} 카드의 관련 URL 형식이 올바르지 않습니다 (http/https 필요): '{url}'")
        if urls:
            print(f"  ✓ {comp} 관련 검증 URL {len(urls)}개 확인 완료")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Daily News Card Builder")
    parser.add_argument("--data", required=True, help="news_data.json 경로")
    parser.add_argument("--publish", action="store_true", help="빌드 후 Instagram/Threads/Telegram 자동 게시")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 뉴스 데이터 유효성 검증
    validate_news_data(data)

    date = data["date"]
    output_dir = os.path.join(SCRIPT_DIR, date)
    os.makedirs(output_dir, exist_ok=True)

    # news_data.json을 빌드 폴더에 복사 (publish.py가 참조할 수 있도록)
    shutil.copy2(args.data, os.path.join(output_dir, "news_data.json"))

    print(f"\n{'='*60}")
    print(f"  Daily News Card Builder — {date}")
    print(f"{'='*60}")

    print(f"\n[1/6] HTML 생성")
    generate_html(data, output_dir)

    print(f"\n[2/6] CSS 생성")
    generate_css(data, output_dir)

    print(f"\n[3/6] 이미지 확보")
    download_images(data, output_dir)

    print(f"\n[4/6] PNG 렌더링")
    export_pngs(data, output_dir)

    print(f"\n[5/6] 빌드 리포트")
    generate_report(data, output_dir)

    print(f"\n[6/6] Downloads 복사")
    copy_to_downloads(data, output_dir)

    print(f"\n{'='*60}")
    print(f"  ✅ 빌드 완료: {output_dir}")
    print(f"  📁 다운로드: ~/Downloads/{date}_daily_news/")
    print(f"{'='*60}\n")

    # ── 자동 게시 ──
    if args.publish:
        publish_script = os.path.join(SCRIPT_DIR, "publish.py")
        print(f"\n{'='*60}")
        print(f"  📡 자동 게시 시작...")
        print(f"{'='*60}")
        subprocess.run(
            [sys.executable, publish_script, "--date", date,
             "--data", os.path.join(output_dir, "news_data.json")],
            cwd=SCRIPT_DIR
        )


if __name__ == "__main__":
    main()


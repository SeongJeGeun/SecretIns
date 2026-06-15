#!/usr/bin/env python3
"""
IT & AI News Media Fusion Tool
===============================
news_data.json 원고에 등록된 교차 검증 기사 URL들(related_urls)을 돌며
가장 문맥에 잘 맞고 해상도가 우수한 실제 실사 이미지를 자동으로 찾아내어
build assets 폴더에 매칭시켜 주는 미디어 융합 분석기입니다.

Usage:
  python3 fuse_news.py
  python3 fuse_news.py --dry-run
"""

import os
import re
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "news_data.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 기각할 이미지 파일명/키워드 패턴 (로고, 아이콘, 아바타, 배너 배제)
EXCLUDE_KEYWORDS = [
    "logo", "icon", "banner", "avatar", "sprite", "nav", "menu", "footer", 
    "button", "placeholder", "default", "spacer", "advertisement", "ad-",
    "theme", "widget", "arrow", "loading", "profile", "comment",
    "ave", "avenue", "promo", "event", "popup", "ad_", "ad-", "main-banner", 
    "sub-banner", "top-", "bottom-", "toyota", "car-", "vehicle"
]


def extract_images_from_html(html_content, base_url):
    """HTML 소스코드에서 og:image 및 일반 img 태그의 주소들을 추출합니다."""
    images = []
    
    # 1. og:image 우선 추출
    og_matches = re.findall(r'<meta\s+[^>]*property=["\']og:image["\'][^>]*content=["\'](.*?)["\']', html_content, re.IGNORECASE)
    if not og_matches:
        og_matches = re.findall(r'<meta\s+[^>]*content=["\'](.*?)["\'][^>]*property=["\']og:image["\']', html_content, re.IGNORECASE)
    
    for img_url in og_matches:
        img_url = img_url.strip()
        if img_url:
            images.append((img_url, True)) # (url, is_og)

    # 2. 일반 img 태그 추출
    img_tags = re.findall(r'<img\s+[^>]*src=["\'](.*?)["\']', html_content, re.IGNORECASE)
    for img_url in img_tags:
        img_url = img_url.strip()
        if img_url and not img_url.startswith("data:"):
            # 중복 회피
            if not any(img_url == existing[0] for existing in images):
                images.append((img_url, False))
                
    # 3. 상대 경로를 절대 경로로 보정
    final_images = []
    for img_url, is_og in images:
        try:
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            elif img_url.startswith("/") and not img_url.startswith("//"):
                img_url = urllib.parse.urljoin(base_url, img_url)
            elif not img_url.startswith("http"):
                img_url = urllib.parse.urljoin(base_url, img_url)
            
            final_images.append((img_url, is_og))
        except Exception:
            pass
            
    return final_images


def is_valid_image_url(url):
    """이미지 URL이 기각 패턴에 속하는지 필터링합니다."""
    url_lower = url.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in url_lower:
            return False
    return True


def download_and_inspect_image(url, temp_path):
    """이미지를 다운로드하여 해상도와 규격을 점검합니다."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as response:
            content = response.read()
            
        with open(temp_path, "wb") as f:
            f.write(content)
            
        with Image.open(temp_path) as img:
            w, h = img.size
            # 규격 조건: 가로 500px 이상이며 가로가 더 긴(혹은 정방형인) 이미지
            if w >= 500 and w >= h:
                return True, w, h
    except Exception:
        pass
        
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass
    return False, 0, 0


def crop_and_resize(src_path, dst_path, w=1080, h=702):
    """이미지를 카드뉴스 규격(1080x702, center crop)에 맞게 가공합니다."""
    try:
        with Image.open(src_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            ow, oh = img.size
            target_ratio = w / h
            current_ratio = ow / oh
            
            if current_ratio > target_ratio:
                # 가로가 더 긴 경우 좌우 자르기
                nw = int(oh * target_ratio)
                left = (ow - nw) // 2
                img = img.crop((left, 0, left + nw, oh))
            else:
                # 세로가 더 긴 경우 상하 자르기
                nh = int(ow / target_ratio)
                top = (oh - nh) // 2
                img = img.crop((0, top, ow, top + nh))
                
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            img.save(dst_path, "PNG")
        return True
    except Exception as e:
        print(f"      ✗ 리사이즈 실패: {e}")
        return False


def process_url(url):
    """URL에 방문해 HTML을 가져옵니다."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode("utf-8", errors="ignore")
        return html_content
    except Exception:
        return ""


def main():
    dry_run = "--dry-run" in sys.argv
    
    if not os.path.exists(DATA_PATH):
        print(f"✗ news_data.json이 존재하지 않습니다: {DATA_PATH}")
        sys.exit(1)
        
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        news_data = json.load(f)
        
    date = news_data.get("date")
    cards = news_data.get("cards", [])
    
    print("\n" + "=" * 60)
    print(f"  다차원 미디어 융합 분석기 가동 — {date} (총 {len(cards)}개 뉴스)")
    print("=" * 60)
    
    build_dir = os.path.join(SCRIPT_DIR, date)
    assets_dir = os.path.join(build_dir, "assets")
    
    if not dry_run:
        os.makedirs(assets_dir, exist_ok=True)
        
    temp_img_path = os.path.join(SCRIPT_DIR, "temp_fuse_img.tmp")
    
    for i, card in enumerate(cards):
        num = str(i + 2).zfill(2)
        theme = card["theme"]
        company = card["company"]
        title = card["title"]
        
        target_filename = f"card_{num}_{theme}.png"
        target_path = os.path.join(assets_dir, target_filename)
        
        print(f"\n  [{num}] {company}: {title}")
        
        # 교차 검증 URL 풀 생성 (related_urls가 없으면 기존 image_url이나 source 활용)
        urls = card.get("related_urls", [])
        if not urls and card.get("source_url"):
            urls = [card["source_url"]]
            
        if not urls:
            print("    ⚠ 교차 기사 URL이 등록되어 있지 않습니다. 자동 검색이 필요합니다.")
            print(f"[MISSING_IMAGE_TRIGGER] card_num={num}, theme={theme}, company={company}, title={title}, query={card.get('image_search')}")
            continue
            
        image_found = False
        
        for url_idx, url in enumerate(urls):
            print(f"    🔎 [{url_idx+1}/{len(urls)}] 교차 기사 웹 분석 중: {url[:60]}...")
            html_content = process_url(url)
            if not html_content:
                print("      ✗ 접속 실패")
                continue
                
            img_candidates = extract_images_from_html(html_content, url)
            print(f"      ✓ 이미지 후보 {len(img_candidates)}개 발견")
            
            # og:image 우선으로 적격성 검증
            # 1회차 루프: og_image 검사 / 2회차 루프: 일반 img 검사
            for check_og in [True, False]:
                if image_found:
                    break
                    
                for img_url, is_og in img_candidates:
                    if is_og != check_og:
                        continue
                        
                    if not is_valid_image_url(img_url):
                        continue
                        
                    if dry_run:
                        print(f"      [Dry-Run] 후보 매칭 검토: {img_url[:70]}")
                        # 첫 번째 적격 후보를 만났다고 가정하고 넘김
                        image_found = True
                        break
                        
                    # 실제 검증 및 다운로드
                    ok, w, h = download_and_inspect_image(img_url, temp_img_path)
                    if ok:
                        print(f"      ✓ 적격 이미지 획득 성공! ({w}x{h}) ➔ {img_url[:50]}...")
                        # 카드뉴스 규격으로 크롭 가공 후 보관
                        crop_ok = crop_and_resize(temp_img_path, target_path)
                        if crop_ok:
                            image_found = True
                            if os.path.exists(temp_img_path):
                                os.remove(temp_img_path)
                            break
                
            if image_found:
                break
                
        if image_found:
            print(f"    ✓ [{num}] 미디어 융합 이미지 매칭 완료.")
        else:
            print(f"    ✗ 적격 이미지를 수집하지 못했습니다.")
            # 플레이스홀더를 만들지 않고 트리거 로그만 던져서 AI 생성을 유도
            print(f"[MISSING_IMAGE_TRIGGER] card_num={num}, theme={theme}, company={company}, title={title}, query={card.get('image_search')}")
            
    print("\n" + "=" * 60)
    print("  ✅ 미디어 융합 분석 완료!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

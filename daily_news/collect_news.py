#!/usr/bin/env python3
"""
IT & AI News Collector
=======================
Google News RSS 및 Hacker News RSS 피드를 통해 최근 24시간 동안의 IT/AI 관련 뉴스를 전수 수집하여
raw_news_pool.json 파일로 저장합니다.

Usage:
  python3 collect_news.py
"""

import os
import sys
import json
import re
import html
import urllib.request
from datetime import datetime

import urllib.parse

# 스크립트 디렉토리 정의
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "raw_news_pool.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# URL 쿼리 파라미터 인코딩
ko_query = urllib.parse.quote("when:24h (AI OR IT OR 테크 OR 반도체)")
en_query = urllib.parse.quote("when:24h (AI OR tech OR technology OR semiconductor)")

FEEDS = {
    "google_news_ko": {
        "url": f"https://news.google.com/rss/search?q={ko_query}&hl=ko&gl=KR&ceid=KR:ko",
        "source_type": "Google News (KR)",
        "language": "ko"
    },
    "google_news_en": {
        "url": f"https://news.google.com/rss/search?q={en_query}&hl=en&gl=US&ceid=US:en",
        "source_type": "Google News (US)",
        "language": "en"
    },
    "hacker_news": {
        "url": "https://hnrss.org/newest?points=50",
        "source_type": "Hacker News",
        "language": "en"
    }
}

def clean_html(text):
    if not text:
        return ""
    # HTML 태그 제거
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # HTML 엔티티 변환 (e.g., &amp; -> &, &quot; -> ")
    return html.unescape(text).strip()

def fetch_feed(name, config):
    url = config["url"]
    print(f"  → [{name}] RSS 피드 가져오는 중: {url}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
        return xml_data
    except Exception as e:
        print(f"  ✗ [{name}] 피드 가져오기 실패: {e}", file=sys.stderr)
        return None

def parse_rss(xml_data, config):
    import xml.etree.ElementTree as ET
    items = []
    try:
        root = ET.fromstring(xml_data)
        channel = root.find("channel")
        if channel is None:
            return items

        for item_node in channel.findall("item"):
            title_node = item_node.find("title")
            link_node = item_node.find("link")
            pub_date_node = item_node.find("pubDate")
            desc_node = item_node.find("description")
            source_node = item_node.find("source")

            title = clean_html(title_node.text) if title_node is not None else ""
            link = link_node.text.strip() if link_node is not None else ""
            pub_date = pub_date_node.text.strip() if pub_date_node is not None else ""
            description = clean_html(desc_node.text) if desc_node is not None else ""
            
            # 출처(언론사) 추출
            publisher = ""
            if source_node is not None and source_node.text:
                publisher = source_node.text.strip()
            elif " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0].strip()
                publisher = parts[1].strip()

            if not title or not link:
                continue

            items.append({
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "description": description[:300], # 요약 설명은 300자까지만 저장
                "publisher": publisher or config["source_type"],
                "source_type": config["source_type"],
                "language": config["language"]
            })
    except Exception as e:
        print(f"  ✗ RSS 파싱 에러: {e}", file=sys.stderr)
    return items

def main():
    print("=" * 60)
    print("  글로벌 & 국내 24시간 IT/AI 뉴스 수집 시작")
    print("=" * 60)

    news_pool = []
    seen_links = set()

    for name, config in FEEDS.items():
        xml_data = fetch_feed(name, config)
        if xml_data:
            items = parse_rss(xml_data, config)
            print(f"    ✓ {len(items)}개 기사 파싱 성공")
            for item in items:
                # 중복 링크 제거
                if item["link"] not in seen_links:
                    seen_links.add(item["link"])
                    news_pool.append(item)

    # 결과물 구조화
    output_data = {
        "collected_at": datetime.now().isoformat(),
        "total_count": len(news_pool),
        "news": news_pool
    }

    # 파일 저장
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"  ✅ 뉴스 수집 완료! 총 {len(news_pool)}개 고유 기사 확보")
    print(f"  📂 저장 위치: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()

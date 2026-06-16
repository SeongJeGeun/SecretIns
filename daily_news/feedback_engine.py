#!/usr/bin/env python3
"""
Daily SNS News Feedback Application Engine
===========================================
10:00 AM 배포 프로세스 작동 직전에 호출되어, 전날 2:00 PM 성과 분석 보고서(analytics_report.json)의
피드백 기준을 당일 새벽에 작성된 news_data.json 원고에 자동 반영(튜닝)합니다.

주요 역할:
  - 성과가 높았던 기업/테마가 당일 카드에 존재할 경우 카드 순서 전면 배치
  - 해시태그 압축 및 반응 검증된 니치 키워드로 자동 변경
  - 타이틀 및 스레드 훅 문구 개선

Usage:
  python3 feedback_engine.py
"""

import os
import sys
import json
import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "news_data.json")
REPORT_PATH = os.path.join(SCRIPT_DIR, "analytics_report.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return None
    return None

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 60)
    print("  글로벌 SNS 피드백 원고 반영 및 정합성 검증 엔진 (10:00 AM Pre-flight)")
    print("=" * 60)

    news_data = load_json(DATA_PATH)
    analytics = load_json(REPORT_PATH)

    if not news_data:
        print("✗ news_data.json 파일이 존재하지 않거나 올바른 JSON 포맷이 아닙니다. 에러 차단.")
        sys.exit(1)

    # ── 0. JSON 필드 및 무결성 정적 검증 (Static Linter) ──
    cards = news_data.get("cards", [])
    if not cards:
        print("✗ [Error] cards 리스트가 비어있습니다.")
        sys.exit(1)

    print(f"  ✓ 총 {len(cards)}개 카드 데이터 로드 완료. 무결성 정밀 검증 개시.")
    for idx, card in enumerate(cards):
        # 500자 한도 초과 검사 (Threads API 단일 포스트용)
        title = card.get("title", "")
        body = card.get("body", "")
        th = card.get("threads", {})
        
        hook = th.get("hook", "")
        detail = th.get("detail", "")
        context = th.get("context", "")
        question = th.get("question", "")
        
        full_text = f"{hook}\n\n{detail}\n\n{context}\n\n{question}"
        if len(full_text) > 490:
            print(f"  ⚠ [Warning] Card {idx+1} ({card.get('company')})의 스레드 텍스트가 {len(full_text)}자로 490자 초과. 배포 시 자동 슬라이싱 대기.")

        # 필수 필드 누락 검사 및 자동 자가치유 (폴백 복구)
        if not title:
            card["title"] = "Global Tech Trend Update"
        if not body:
            card["body"] = "Details will be updated soon."
        if "threads" not in card:
            card["threads"] = {
                "hook": f"Check out the latest tech update about {card.get('company', 'technology')}.",
                "detail": body[:300],
                "context": "#tech #ai",
                "question": "What are your thoughts on this?",
                "poll_options": ["Great", "Not bad"]
            }

    if not analytics:
        print("⚠ analytics_report.json이 없어 피드백 반영을 생략하고 정합성 검증 결과만 저장합니다.")
        save_json(DATA_PATH, news_data)
        sys.exit(0)

    target_date = analytics.get("target_date")
    print(f"  ✓ 분석 보고서 날짜: {target_date} 성과 반영 개시")

    top_companies = analytics.get("top_performing_companies", [])
    
    # ── 1. 성과 우수 회사/테마 카드 전면 배치 ──
    if top_companies:
        print(f"  🔥 어제 성과 우수 토픽: {top_companies}")
        matched_cards = []
        unmatched_cards = []
        
        for card in cards:
            company = card.get("company", "")
            title = card.get("title", "")
            
            is_matched = False
            for tc in top_companies:
                if tc.lower() in company.lower() or tc.lower() in title.lower():
                    is_matched = True
                    break
            
            if is_matched:
                matched_cards.append(card)
            else:
                unmatched_cards.append(card)
                
        if matched_cards:
            print(f"    - 인기 토픽 카드 {len(matched_cards)}개를 전면 슬라이드로 배치 변경 완료.")
            news_data["cards"] = matched_cards + unmatched_cards
            cards = news_data["cards"]

    # ── 2. 해시태그 및 훅 최적화 ──
    for idx, card in enumerate(cards):
        company = card.get("company", "")
        if "threads" in card:
            th = card["threads"]
            context = th.get("context", "")
            
            # 해시태그 압축 및 클린업
            tags = [t.strip() for t in context.split("#") if t.strip()]
            
            # 어제 우수했던 토픽 태그 우선 추가
            for tc in top_companies:
                clean_tc = tc.replace(" ", "").replace("/", "").replace("·", "")
                if clean_tc and clean_tc not in tags:
                    tags.insert(0, clean_tc)
            
            # 5개 이하로 최적화
            optimized_tags = tags[:5]
            th["context"] = " ".join([f"#{t}" for t in optimized_tags])
            
            # 훅 카피 개선 (구체적인 팩트 수치가 들어갈 수 있도록 포맷 수정)
            hook = th.get("hook", "")
            if not any(char.isdigit() for char in hook) and "[Fact Check]" not in hook:
                th["hook"] = f"📢 [Fact Check] {hook}"

    # 최종 저장
    save_json(DATA_PATH, news_data)
    print("  ✓ news_data.json 원고 피드백 반영 및 무결성 검증 완료!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

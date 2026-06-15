#!/usr/bin/env python3
"""
IT & AI Media OS - Comment & Reply Manager
===========================================
인스타그램 및 스레드에서 외부 독자들이 남긴 댓글/대댓글을 수집하고,
자체 내장 LLM(안티그래비티)이 작성한 답글을 API를 통해 게시하는 도구입니다.

Usage:
  # 미답변 댓글 조회
  python3 comment_manager.py --fetch
  
  # 특정 댓글에 답글 작성
  python3 comment_manager.py --reply --platform instagram --id [ID] --message "답변 내용"
  python3 comment_manager.py --reply --platform threads --id [ID] --message "답변 내용"
"""

import os
import sys
import json
import argparse
import requests
import datetime
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# ─── 환경 변수 ───
IG_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
THREADS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
TG_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 본인 계정명 정의 (필터링용)
IG_SELF_USERNAME = os.getenv("INSTAGRAM_USERNAME", "mind_factory_news")
THREADS_SELF_USERNAME = "mind_factory_news"

HISTORY_PATH = os.path.join(SCRIPT_DIR, "publish_history.json")

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def get_instagram_unanswered_comments(media_id):
    """인스타그램 미답변 댓글 수집"""
    unanswered = []
    if not IG_TOKEN or not media_id:
        return unanswered

    try:
        url = f"https://graph.facebook.com/v19.0/{media_id}/comments"
        res = requests.get(url, params={"fields": "id,text,username", "access_token": IG_TOKEN}, timeout=15)
        comments = res.json().get("data", [])

        for c in comments:
            c_id = c.get("id")
            c_text = c.get("text", "")
            c_user = c.get("username", "")

            # 본인 댓글은 제외
            if c_user == IG_SELF_USERNAME:
                continue

            # 이미 대댓글을 달았는지 확인
            replies_url = f"https://graph.facebook.com/v19.0/{c_id}/replies"
            res_rep = requests.get(replies_url, params={"fields": "id,username", "access_token": IG_TOKEN}, timeout=15)
            replies = res_rep.json().get("data", [])

            already_replied = False
            for r in replies:
                if r.get("username") == IG_SELF_USERNAME:
                    already_replied = True
                    break

            if not already_replied:
                unanswered.append({
                    "platform": "instagram",
                    "comment_id": c_id,
                    "username": c_user,
                    "text": c_text
                })
    except Exception as e:
        print(f"  ⚠ 인스타 댓글 수집 중 오류: {e}")

    return unanswered

def get_threads_unanswered_replies(threads):
    """스레드 미답변 댓글(대댓글) 수집"""
    unanswered = []
    if not THREADS_TOKEN or not threads:
        return unanswered

    try:
        for th in threads:
            node_id = th.get("root_id")
            comp = th.get("company", "Unknown")
            if not node_id:
                continue

            url = f"https://graph.threads.net/v1.0/{node_id}/replies"
            res = requests.get(url, params={"fields": "id,text,username", "access_token": THREADS_TOKEN}, timeout=15)
            replies = res.json().get("data", [])

            for r in replies:
                r_id = r.get("id")
                r_text = r.get("text", "")
                r_user = r.get("username", "")

                # 본인 작성 글(체인 등)은 제외
                if r_user == THREADS_SELF_USERNAME:
                    continue

                # 이미 우리가 답글을 달아주었는지 확인
                child_url = f"https://graph.threads.net/v1.0/{r_id}/replies"
                res_child = requests.get(child_url, params={"fields": "id,username", "access_token": THREADS_TOKEN}, timeout=15)
                child_replies = res_child.json().get("data", [])

                already_replied = False
                for cr in child_replies:
                    if cr.get("username") == THREADS_SELF_USERNAME:
                        already_replied = True
                        break

                if not already_replied:
                    unanswered.append({
                        "platform": "threads",
                        "comment_id": r_id,
                        "username": r_user,
                        "text": r_text,
                        "topic": comp
                    })
    except Exception as e:
        print(f"  ⚠ 스레드 댓글 수집 중 오류: {e}")

    return unanswered

def post_instagram_reply(comment_id, message):
    """인스타그램 댓글에 답글 작성"""
    if not IG_TOKEN:
        raise Exception("INSTAGRAM_ACCESS_TOKEN 이 존재하지 않습니다.")
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
    res = requests.post(url, params={"message": message, "access_token": IG_TOKEN}, timeout=15)
    data = res.json()
    if "id" in data:
        return data["id"]
    else:
        raise Exception(f"인스타 답글 작성 실패: {data}")

def post_threads_reply(reply_to_id, message):
    """스레드 대댓글 작성"""
    if not THREADS_TOKEN:
        raise Exception("THREADS_ACCESS_TOKEN 이 존재하지 않습니다.")
    
    # 1. 컨테이너 생성
    url_container = "https://graph.threads.net/v1.0/me/threads"
    payload = {
        "media_type": "TEXT",
        "text": message,
        "reply_to_id": reply_to_id,
        "access_token": THREADS_TOKEN
    }
    res_c = requests.post(url_container, data=payload, timeout=15)
    data_c = res_c.json()
    if "id" not in data_c:
        raise Exception(f"스레드 답글 컨테이너 생성 실패: {data_c}")
    
    creation_id = data_c["id"]
    time_sleep = 5
    print(f"      - 컨테이너 생성 완료 (ID: {creation_id}). {time_sleep}초 대기...")
    import time
    time.sleep(time_sleep)

    # 2. 발행
    url_publish = "https://graph.threads.net/v1.0/me/threads_publish"
    res_p = requests.post(url_publish, data={"creation_id": creation_id, "access_token": THREADS_TOKEN}, timeout=15)
    data_p = res_p.json()
    if "id" in data_p:
        return data_p["id"]
    else:
        raise Exception(f"스레드 답글 발행 실패: {data_p}")

def send_telegram_notification(platform, username, origin_text, reply_text):
    """대댓글 작성 완료 텔레그램 보고"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return False
    
    plat_label = "📸 Instagram" if platform == "instagram" else "🧵 Threads"
    message = (
        f"💬 <b>AI 대댓글 소통 완료 보고</b>\n"
        f"────────────────\n"
        f"🌐 플랫폼: {plat_label}\n"
        f"👤 대상 독자: @{username}\n"
        f"📝 원본 댓글: {origin_text[:50]}...\n"
        f"✨ AI 답글: {reply_text}\n"
        f"────────────────\n"
        f"🤖 IT Media OS 자동화"
    )
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=10
        )
        return True
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="SNS Comment Manager Utility")
    parser.add_argument("--fetch", action="store_true", help="Fetch unanswered comments for today's posts")
    parser.add_argument("--reply", action="store_true", help="Post a reply to a comment")
    parser.add_argument("--platform", choices=["instagram", "threads"], help="Target platform for reply")
    parser.add_argument("--id", help="Target comment ID to reply to")
    parser.add_argument("--message", help="Reply message content")

    args = parser.parse_args()

    if not args.fetch and not args.reply:
        parser.print_help()
        sys.exit(0)

    history = load_history()
    if not history:
        print("✗ 게시 이력(publish_history.json)이 비어 있어 댓글 수집 대상을 특정할 수 없습니다.")
        sys.exit(1)

    # 당일 발행된 최근 포스트 확인
    today_str = datetime.date.today().isoformat()
    today_entries = [e for e in history if e.get("date") == today_str]
    
    if not today_entries:
        print(f"⚠ 오늘 자({today_str}) 게시글 이력이 없습니다. 가장 최근 게시글 기준으로 대상을 검색합니다.")
        today_entry = history[-1]
    else:
        today_entry = today_entries[-1]

    date = today_entry.get("date")
    print(f"🎯 대상 분석 날짜: {date}")

    if args.fetch:
        print("🔍 미답변 독자 댓글 수집 중...")
        
        # 인스타그램 댓글 수집
        ig_media_id = today_entry.get("instagram_id")
        ig_comments = get_instagram_unanswered_comments(ig_media_id)
        
        # 스레드 댓글 수집
        threads = today_entry.get("threads", [])
        threads_replies = get_threads_unanswered_replies(threads)

        all_unanswered = ig_comments + threads_replies

        print(f"✅ 미답변 독자 댓글 총 {len(all_unanswered)}개 감지됨.\n")
        
        if all_unanswered:
            print(f"{'Platform':<12} | {'Comment ID':<20} | {'Username':<18} | {'Topic/Content'}")
            print("-" * 85)
            for item in all_unanswered:
                plat = item["platform"].upper()
                cid = item["comment_id"]
                user = item["username"]
                topic_info = f"({item['topic']}) " if "topic" in item else ""
                content = f"{topic_info}{item['text']}".replace("\n", " ")
                if len(content) > 40:
                    content = content[:38] + "..."
                print(f"{plat:<12} | {cid:<20} | @{user:<17} | {content}")
            print("-" * 85)
            print("\n[AI 실행 가이드] 위 목록의 댓글 ID와 플랫폼을 참고하여 대댓글 전송 명령을 실행하십시오.")
        else:
            print("🎉 모든 독자 댓글에 완벽하게 답글이 달려 있습니다! 대기 중인 새 댓글이 없습니다.")

    elif args.reply:
        if not args.platform or not args.id or not args.message:
            print("✗ 에러: --reply 시 --platform, --id, --message 파라미터는 필수입니다.")
            sys.exit(1)

        print(f"🚀 {args.platform.upper()} 댓글 [{args.id}]에 답글 전송 시작...")
        
        try:
            # 원본 댓글의 작성자명을 텔레그램 보고용으로 조회 시도
            username = "Reader"
            origin_text = "Unknown Comment"
            
            if args.platform == "instagram":
                # 인스타그램 원본 댓글 텍스트 및 유저 조회를 위한 페치
                try:
                    res_c = requests.get(f"https://graph.facebook.com/v19.0/{args.id}", params={"fields": "text,username", "access_token": IG_TOKEN}, timeout=10)
                    data_c = res_c.json()
                    username = data_c.get("username", "Reader")
                    origin_text = data_c.get("text", "Unknown Comment")
                except Exception:
                    pass
                
                post_instagram_reply(args.id, args.message)
            else:
                # 스레드 원본 댓글 텍스트 및 유저 조회를 위한 페치
                try:
                    res_c = requests.get(f"https://graph.threads.net/v1.0/{args.id}", params={"fields": "text,username", "access_token": THREADS_TOKEN}, timeout=10)
                    data_c = res_c.json()
                    username = data_c.get("username", "Reader")
                    origin_text = data_c.get("text", "Unknown Comment")
                except Exception:
                    pass
                
                post_threads_reply(args.id, args.message)

            print("✅ 답글 등록 및 실서버 발행 완료!")
            
            # 텔레그램 보고 전송
            send_telegram_notification(args.platform, username, origin_text, args.message)
            print("  ✓ Telegram 전송 성공")

        except Exception as e:
            print(f"✗ 답글 작성 중 에러 발생: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Daily News Auto Publisher
==========================
빌드 결과물을 Instagram, Threads, Telegram에 자동 게시합니다.
Threads는 텍스트 포스트 형식으로 게시합니다.
중복 업로드를 자동으로 방지합니다.

Usage:
  python3 publish.py --date 2026-06-08
  python3 publish.py --date 2026-06-08 --skip-instagram --skip-threads
"""

import os
import sys
import json
import time
import argparse
import shutil

import requests
from dotenv import load_dotenv

# .env 로드
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

# ─── 환경 변수 ───
IG_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
THREADS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
TG_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

HISTORY_PATH = os.path.join(SCRIPT_DIR, "publish_history.json")


# ============================================================
# 0. 중복 방지 (Publish History)
# ============================================================
def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def is_duplicate(date, mode):
    """같은 날짜 + 모드 조합이 이미 게시됐는지 확인"""
    history = load_history()
    for entry in history:
        if entry.get("date") == date and entry.get("mode") == mode:
            return True, entry
    return False, None


def record_publish(date, mode, ig_result, threads_results, telegram_ok):
    """게시 이력 기록"""
    from datetime import datetime
    history = load_history()
    
    threads_list = []
    if threads_results:
        for r in threads_results:
            if r.get("status") == "success":
                threads_list.append({
                    "company": r.get("company"),
                    "root_id": r.get("root_id")
                })
                
    history.append({
        "date": date,
        "mode": mode,
        "published_at": datetime.now().isoformat(),
        "instagram_id": ig_result,
        "threads": threads_list,
        "threads_count": len(threads_list),
        "telegram": telegram_ok,
    })
    save_history(history)
    print(f"  ✓ 게시 이력 기록 완료 ({date}/{mode})")


# ============================================================
# 1. 이미지 호스팅 (Catbox.moe)
# ============================================================
def upload_to_catbox(file_path):
    """로컬 PNG를 uguu.se에 우선 업로드하고, 실패 시 Catbox에 업로드하여 공개 URL 반환 (최대 3회 재시도)"""
    print(f"    ↑ {os.path.basename(file_path)}")
    max_retries = 3
    
    # 1. uguu.se 업로드 시도 (인스타그램 타임아웃 방지용 고속 임시 호스팅)
    for attempt in range(1, max_retries + 1):
        try:
            with open(file_path, "rb") as f:
                res = requests.post(
                    "https://uguu.se/upload.php",
                    files={"files[]": f},
                    timeout=15
                )
            if res.status_code == 200:
                data = res.json()
                if data.get("success") and data.get("files"):
                    url = data["files"][0]["url"]
                    print(f"      → {url} (via uguu.se, 시도 {attempt})")
                    return url
        except Exception as e:
            print(f"      ⚠ uguu.se 업로드 시도 {attempt} 실패: {e}")
            if attempt < max_retries:
                time.sleep(2)

    print("      ⚠ uguu.se 업로드 최종 실패, Catbox로 폴백합니다.")

    # 2. Catbox.moe 폴백 업로드 시도
    for attempt in range(1, max_retries + 1):
        try:
            with open(file_path, "rb") as f:
                res = requests.post(
                    "https://catbox.moe/user/api.php",
                    data={"reqtype": "fileupload"},
                    files={"fileToUpload": f},
                    timeout=30
                )
            if res.status_code == 200 and res.text.startswith("https://"):
                url = res.text.strip()
                print(f"      → {url} (via Catbox, 시도 {attempt})")
                return url
        except Exception as e:
            print(f"      ⚠ Catbox 업로드 시도 {attempt} 실패: {e}")
            if attempt < max_retries:
                time.sleep(2)

    raise Exception("모든 파일 호스팅 업로드 최종 실패")


# ============================================================
# 2. Instagram 캐러셀 게시
# ============================================================
def get_instagram_account_id():
    res = requests.get(
        "https://graph.facebook.com/v19.0/me/accounts",
        params={"access_token": IG_TOKEN},
    )
    pages = res.json().get("data", [])
    for page in pages:
        ig_res = requests.get(
            f"https://graph.facebook.com/v19.0/{page['id']}",
            params={"fields": "instagram_business_account", "access_token": IG_TOKEN},
        )
        ig_data = ig_res.json()
        if "instagram_business_account" in ig_data:
            return ig_data["instagram_business_account"]["id"]
    raise Exception("Instagram Business Account를 찾을 수 없습니다.")


def publish_instagram(image_urls, caption):
    print("\n  [Instagram] 게시 시작...")
    ig_id = get_instagram_account_id()
    print(f"    Account ID: {ig_id}")

    container_ids = []
    for i, url in enumerate(image_urls):
        print(f"    컨테이너 생성 {i+1}/{len(image_urls)}...")
        
        max_retries = 3
        retry_delay = 5  # 초기 대기 시간 (초)
        for attempt in range(1, max_retries + 1):
            try:
                res = requests.post(
                    f"https://graph.facebook.com/v19.0/{ig_id}/media",
                    data={
                        "image_url": url,
                        "is_carousel_item": "true",
                        "access_token": IG_TOKEN,
                    },
                    timeout=20
                )
                data = res.json()
                if "id" in data:
                    container_ids.append(data["id"])
                    break
                else:
                    raise Exception(f"컨테이너 응답 오류: {data}")
            except Exception as e:
                print(f"      ⚠ 컨테이너 생성 실패 (시도 {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise Exception(f"컨테이너 생성 최종 실패: {e}")
                wait_time = retry_delay * (2 ** (attempt - 1))
                print(f"      ➔ {wait_time}초 후 재시도합니다...")
                time.sleep(wait_time)
        
        # 이미지 컨테이너 간 기본 대기 시간을 2초에서 6초로 증가
        time.sleep(6)

    print("    캐러셀 컨테이너 생성...")
    max_retries = 3
    carousel_id = None
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.post(
                f"https://graph.facebook.com/v19.0/{ig_id}/media",
                data={
                    "media_type": "CAROUSEL",
                    "children": json.dumps(container_ids),
                    "caption": caption,
                    "access_token": IG_TOKEN,
                },
                timeout=20
            )
            carousel_data = res.json()
            if "id" in carousel_data:
                carousel_id = carousel_data["id"]
                break
            else:
                raise Exception(f"캐러셀 생성 응답 오류: {carousel_data}")
        except Exception as e:
            print(f"      ⚠ 캐러셀 생성 실패 (시도 {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                raise Exception(f"캐러셀 생성 최종 실패: {e}")
            wait_time = 10 * attempt
            print(f"      ➔ {wait_time}초 후 재시도합니다...")
            time.sleep(wait_time)

    # 대기 시간을 10초에서 20초로 증가 (인스타그램 미디어 처리 안정성)
    print("    이미지 처리 대기 (20초)...")
    time.sleep(20)

    # 3. 최종 게시 요청 (1차)
    print("    최종 게시 요청 (media_publish)...")
    published_successfully = False
    published_id = None
    try:
        res = requests.post(
            f"https://graph.facebook.com/v19.0/{ig_id}/media_publish",
            data={"creation_id": carousel_id, "access_token": IG_TOKEN},
            timeout=20
        )
        pub_data = res.json()
        if "id" in pub_data:
            print(f"    ✓ 1차 게시 요청 응답 성공! ID: {pub_data['id']}")
            published_successfully = True
            published_id = pub_data["id"]
        else:
            print(f"    ⚠ 1차 게시 요청 응답 에러 (백그라운드 처리 확인 대기): {pub_data}")
    except Exception as e:
        print(f"    ⚠ 1차 게시 요청 실패: {e}")

    # 4. 동적 대기 (15초 * 이미지 장수)
    wait_time = len(image_urls) * 15
    print(f"    ⏳ 인스타그램 미디어 백그라운드 처리 동적 대기 시작 ({wait_time}초)...")
    time.sleep(wait_time)

    # 5. 피드 리스트 확인 (사후 검증)
    print("    🔍 인스타그램 피드 리스트 조회하여 실제 발행 여부 검증 중...")
    try:
        res_media = requests.get(
            f"https://graph.facebook.com/v19.0/{ig_id}/media",
            params={
                "fields": "id,caption",
                "access_token": IG_TOKEN
            },
            timeout=20
        )
        media_list_data = res_media.json()
        
        # 캡션 앞 30글자를 매칭 키로 사용
        match_key = caption[:30].strip()
        
        # 최근 5개의 피드 중 캡션이 겹치는 글이 실제로 올라왔는지 검증
        for media in media_list_data.get("data", [])[:5]:
            med_caption = media.get("caption", "")
            if match_key in med_caption:
                print(f"  ✓ Instagram 피드 실제 발행 확인 완료! Media ID: {media['id']}")
                return media["id"]
        
        # 피드에선 못 찾았지만 1차 응답이 정상적으로 통과했었다면 정상 발행으로 간주
        if published_successfully:
            print(f"  ✓ Instagram 1차 응답 성공 기준 발행 완료 처리 (ID: {published_id})")
            return published_id
            
        raise Exception("인스타그램 피드 리스트에서 오늘 자 뉴스 게시글을 발견하지 못했습니다.")
        
    except Exception as e:
        print(f"  ✗ Instagram 발행 최종 검증 실패: {e}")
        if published_successfully:
            return published_id
        raise e


# ============================================================
# 3. Threads 텍스트 포스트 게시
# ============================================================
def get_threads_user_id():
    res = requests.get(
        "https://graph.threads.net/v1.0/me",
        params={"access_token": THREADS_TOKEN},
    )
    data = res.json()
    if "id" in data:
        return data["id"]
    raise Exception(f"Threads 사용자 ID 조회 실패: {data}")


def create_and_publish_thread(user_id, text, reply_to_id=None, poll_options=None):
    """Threads 텍스트 게시물 1개를 생성하고 발행, media_id 반환"""
    payload = {
        "media_type": "TEXT",
        "text": text,
        "access_token": THREADS_TOKEN,
    }
    if reply_to_id:
        payload["reply_to_id"] = reply_to_id

    if poll_options:
        poll_attachment = {}
        option_keys = ["option_a", "option_b", "option_c", "option_d"]
        for k, opt in zip(option_keys, poll_options[:4]):
            encoded = opt.encode('utf-8')
            if len(encoded) > 24:
                opt = encoded[:24].decode('utf-8', errors='ignore').strip()
            poll_attachment[k] = opt
        payload["poll_attachment"] = json.dumps(poll_attachment, ensure_ascii=False)

    # 컨테이너 생성
    res = requests.post(
        f"https://graph.threads.net/v1.0/{user_id}/threads",
        data=payload,
    )
    data = res.json()
    if "id" not in data:
        raise Exception(f"컨테이너 생성 실패: {data}")

    creation_id = data["id"]
    time.sleep(5)

    # 발행
    res = requests.post(
        f"https://graph.threads.net/v1.0/{user_id}/threads_publish",
        data={"creation_id": creation_id, "access_token": THREADS_TOKEN},
    )
    pub_data = res.json()
    if "id" in pub_data:
        return pub_data["id"]
    else:
        raise Exception(f"발행 실패: {pub_data}")


def build_thread_single_from_card(card):
    """news_data.json의 card 데이터에서 Threads 텍스트 포스트 생성 (500자 이내)"""
    status_emoji = "✅" if card["status"] == "official" else "📰"
    company = card["company"]

    if "threads" in card:
        t = card["threads"]
        hook = t.get("hook", "").strip()
        detail = t.get("detail", "").strip()
        context = t.get("context", "").strip()
        question = t.get("question", "").strip()
        
        parts = []
        if hook: parts.append(hook)
        if detail: parts.append(detail)
        if context: parts.append(context)
        if question: parts.append(question)
        
        single_text = "\n\n".join(parts)
    else:
        # 자동 생성 폴백 (500자 이내로 정돈)
        single_text = (
            f"🔔 {status_emoji} [{company}] {card['title']}\n\n"
            f"{card['body']}\n\n"
            f"📎 출처: {card['source']}\n"
            f"#IT뉴스 #AI뉴스 #{company.replace(' ', '').replace('/', '')} #테크트렌드"
        )
        
    # 만약 500자 제한을 초과하는 경우 안전하게 슬라이싱
    if len(single_text) > 490:
        single_text = single_text[:487] + "..."
        
    return single_text


def publish_threads(news_cards, date):
    """각 뉴스 데이터별 Threads 텍스트 포스트 게시"""
    print("\n  [Threads] 텍스트 포스트 게시 시작...")
    user_id = get_threads_user_id()
    print(f"    User ID: {user_id}")

    results = []
    for i, card in enumerate(news_cards):
        company = card["company"]
        post_text = build_thread_single_from_card(card)

        print(f"\n    [{i+1}/{len(news_cards)}] {company} (텍스트 포스트)")

        try:
            poll_opts = None
            if "threads" in card and "poll_options" in card["threads"]:
                poll_opts = card["threads"]["poll_options"]
                print(f"      (투표 활성화: {poll_opts})")
                
            post_id = create_and_publish_thread(user_id, post_text, reply_to_id=None, poll_options=poll_opts)
            print(f"      ✓ ID: {post_id}")

            results.append({
                "company": company,
                "root_id": post_id,
                "post_count": 1,
                "status": "success",
            })
            print(f"      ✓ {company} 게시 완료")

        except Exception as e:
            print(f"      ✗ 실패: {e}")
            results.append({
                "company": company,
                "error": str(e),
                "status": "failed",
            })

        time.sleep(5)

    success = sum(1 for r in results if r["status"] == "success")
    print(f"\n  ✓ Threads 텍스트 포스트 게시 완료: {success}/{len(news_cards)}개 성공")
    return results


# ============================================================
# 4. Telegram 결과 보고
# ============================================================
def send_telegram_report(date, mode, news_cards, ig_result, threads_results):
    print("\n  [Telegram] 결과 보고 전송...")
    import html

    mode_label = "📰 일일 브리핑" if mode == "daily" else "🔍 이벤트 딥다이브"
    news_list = ""
    for i, card in enumerate(news_cards):
        emoji = "✅" if card["status"] == "official" else "📰"
        safe_company = html.escape(card.get('company', ''))
        safe_title = html.escape(card.get('title', ''))
        news_list += f"  {i+1}. {emoji} {safe_company}: {safe_title}\n"

    ig_status = f"✅ 게시 완료 (ID: {ig_result})" if ig_result else "❌ 실패 또는 건너뜀"

    if threads_results:
        t_success = sum(1 for r in threads_results if r["status"] == "success")
        t_total = len(threads_results)
        posts = sum(r.get("post_count", 0) for r in threads_results if r["status"] == "success")
        threads_status = f"✅ {t_success}/{t_total}개 텍스트 포스트 게시 (총 {posts}개 포스트)"
    else:
        threads_status = "⏭ 건너뜀"

    message = (
        f"📢 [{date}] Daily News 게시 보고\n"
        f"{'─' * 30}\n"
        f"📋 모드: {mode_label}\n\n"
        f"📋 뉴스 {len(news_cards)}건:\n{news_list}\n"
        f"📸 Instagram: {ig_status}\n"
        f"🧵 Threads: {threads_status}\n\n"
        f"{'─' * 30}\n"
        f"🤖 IT Media OS 자동 보고"
    )

    res = requests.post(
        f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
        data={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"},
    )
    data = res.json()
    if data.get("ok"):
        print(f"  ✓ Telegram 보고 전송 완료")
    else:
        print(f"  ✗ Telegram 전송 실패: {data}")
    return data.get("ok", False)


def send_telegram_image(image_path, caption=""):
    if not os.path.exists(image_path):
        return
    print("  [Telegram] 콘택트 시트 전송...")
    file_size = os.path.getsize(image_path)
    
    if file_size <= 10 * 1024 * 1024:
        method = "sendPhoto"
        file_key = "photo"
    else:
        print(f"    ⚠ 파일 크기가 {file_size} bytes로 10MB를 초과하여 sendDocument로 전송합니다.")
        method = "sendDocument"
        file_key = "document"
        
    with open(image_path, "rb") as f:
        res = requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/{method}",
            data={"chat_id": TG_CHAT_ID, "caption": caption},
            files={file_key: f},
        )
    if res.json().get("ok"):
        print(f"  ✓ 콘택트 시트 전송 완료 ({method})")
    else:
        print(f"  ✗ 이미지 전송 실패: {res.json()}")


def has_successful_content_publish(ig_result, threads_results):
    if ig_result:
        return True
    if threads_results:
        return any(r.get("status") == "success" for r in threads_results)
    return False


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Daily News Auto Publisher")
    parser.add_argument("--date", required=True, help="발행 날짜 (YYYY-MM-DD)")
    parser.add_argument("--data", default=None, help="news_data.json 경로")
    parser.add_argument("--skip-instagram", action="store_true")
    parser.add_argument("--skip-threads", action="store_true")
    parser.add_argument("--skip-telegram", action="store_true")
    parser.add_argument("--force", action="store_true", help="중복 검사 무시하고 강제 게시")
    parser.add_argument("--clean", action="store_true", help="발행 완료 후 로컬 빌드 파일 및 임시 다운로드 폴더 자동 삭제")
    args = parser.parse_args()

    date = args.date
    build_dir = os.path.join(SCRIPT_DIR, date)
    output_dir = os.path.join(build_dir, "output")

    # news_data.json 찾기
    data_path = args.data
    if not data_path:
        for candidate in [
            os.path.join(build_dir, "news_data.json"),
            os.path.join(SCRIPT_DIR, f"{date}_news_data.json"),
        ]:
            if os.path.exists(candidate):
                data_path = candidate
                break
    if not data_path or not os.path.exists(data_path):
        print(f"✗ news_data.json을 찾을 수 없습니다.")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        news_data = json.load(f)

    cards = news_data["cards"]
    mode = news_data.get("mode", "daily")

    print(f"\n{'='*60}")
    print(f"  Daily News Publisher — {date} ({mode})")
    print(f"{'='*60}")

    # ── 중복 검사 ──
    if not args.force:
        dup, entry = is_duplicate(date, mode)
        if dup:
            print(f"\n  ⚠ 중복 감지! {date}/{mode}는 이미 게시됨")
            print(f"    게시 시각: {entry.get('published_at', '?')}")
            print(f"    --force 옵션으로 강제 게시 가능")
            print(f"\n{'='*60}\n")
            sys.exit(0)

    # ── 이미지 파일 사전 검증 ──
    png_files = []
    if not args.skip_instagram or not args.skip_telegram:
        if not os.path.isdir(output_dir):
            print(f"✗ output 디렉토리를 찾을 수 없습니다: {output_dir}")
            sys.exit(1)

        png_files = sorted([
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.startswith(f"{date}_card_") and f.endswith(".png")
        ])
        expected_count = len(cards) + 2
        print(f"\n  카드 이미지: {len(png_files)}장")

        if not args.skip_instagram and len(png_files) != expected_count:
            print(f"✗ PNG 개수 불일치: {len(png_files)}장 발견, 예상 {expected_count}장")
            sys.exit(1)
    else:
        print("\n  카드 이미지 검증 건너뜀")

    # ── Instagram ──
    ig_result = None
    if not args.skip_instagram:
        try:
            print("\n  [Catbox] 이미지 업로드 중...")
            public_urls = []
            for fp in png_files:
                url = upload_to_catbox(fp)
                public_urls.append(url)
                time.sleep(1)

            n = len(cards)
            if mode == "event":
                event_title = news_data.get("event_title", "이벤트 뉴스")
                caption_lines = [f"{event_title} 📢\n"]
                caption_lines.append(f"핵심 발표 {n}건을 카드뉴스로 정리했습니다.\n")
            else:
                caption_lines = [f"오늘의 IT & AI 뉴스 브리핑 📢\n"]
                caption_lines.append(f"확인된 글로벌 IT/AI 핵심 소식 {n}개를 정리했습니다.\n")

            for i, card in enumerate(cards):
                emoji = "✅" if card["status"] == "official" else "📰"
                caption_lines.append(f"{i+1}. {card['company']}: {card['title']}")
                
            # 동적 해시태그 중합 (각 카드의 스레드 해시태그 풀 활용)
            injected_tags = set()
            for card in cards:
                if "threads" in card and "context" in card["threads"]:
                    context_tags = [t.strip() for t in card["threads"]["context"].split("#") if t.strip()]
                    for tag in context_tags:
                        injected_tags.add(tag)
            
            if injected_tags:
                tag_str = "\n" + " ".join([f"#{t}" for t in sorted(list(injected_tags))])
                caption_lines.append(tag_str)
            else:
                caption_lines.append("\n#IT뉴스 #AI뉴스 #테크트렌드 #인공지능 #테크브리핑")
                
            caption = "\n".join(caption_lines)

            ig_result = publish_instagram(public_urls, caption)
        except Exception as e:
            print(f"  ✗ Instagram 게시 실패: {e}")
    else:
        print("\n  [Instagram] 건너뜀")

    # ── Threads ──
    threads_results = None
    if not args.skip_threads:
        try:
            threads_results = publish_threads(cards, date)
        except Exception as e:
            print(f"  ✗ Threads 게시 실패: {e}")
    else:
        print("\n  [Threads] 건너뜀")

    # ── Telegram ──
    telegram_ok = False
    if not args.skip_telegram:
        try:
            telegram_ok = send_telegram_report(date, mode, cards, ig_result, threads_results)
            sheet_path = os.path.join(output_dir, "contact_sheet.png")
            send_telegram_image(sheet_path, f"📊 {date} 콘택트 시트")
        except Exception as e:
            print(f"  ✗ Telegram 보고 실패: {e}")
    else:
        print("\n  [Telegram] 건너뜀")

    # ── 게시 이력 기록 ──
    if has_successful_content_publish(ig_result, threads_results):
        record_publish(date, mode, ig_result, threads_results, telegram_ok)
    else:
        print("  ⚠ Instagram/Threads 게시 성공 항목이 없어 게시 이력 기록을 생략합니다.")

    # ── 로컬 파일 정리 (Clean up) ──
    if args.clean:
        try:
            print("\n  [Clean up] 로컬 임시 파일 삭제 중...")
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
                print(f"    ✓ 빌드 디렉토리 삭제 완료")
            
            dl_dir = os.path.expanduser(f"~/Downloads/{date}_daily_news")
            if os.path.exists(dl_dir):
                shutil.rmtree(dl_dir)
                print(f"    ✓ 다운로드 디렉토리 삭제 완료")
        except Exception as e:
            print(f"    ✗ 파일 정리 실패: {e}")
    else:
        print("\n  [Clean up] 로컬 빌드 파일 및 다운로드 디렉토리를 보존합니다. (삭제하려면 --clean 옵션 사용)")

    print(f"\n{'='*60}")
    print(f"  ✅ 게시 및 정리 완료! ({date}/{mode})")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

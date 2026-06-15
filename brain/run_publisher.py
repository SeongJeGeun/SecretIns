import os
import sys
import json
import subprocess
from datetime import datetime

# 경로 설정
BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BRAIN_DIR)
DAILY_NEWS_DIR = os.path.join(PROJECT_ROOT, "daily_news")
DRAFT_PATH = os.path.join(DAILY_NEWS_DIR, "news_data_draft.json")
FINAL_PATH = os.path.join(DAILY_NEWS_DIR, "news_data.json")

# 환경 변수 로드
def load_scheduler_env():
    env_path = os.path.join(PROJECT_ROOT, ".secrets", ".env.scheduler")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val

load_scheduler_env()

def send_telegram(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("[Telegram Alert] 설정이 누락되어 메시지를 전송하지 못했습니다.")
        return
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram Alert] 에러: {e}")

def run_build_and_publish():
    print("🚀 [14:00 배포] 카드뉴스 빌드 및 자동 게시를 시작합니다.")
    build_script = os.path.join(DAILY_NEWS_DIR, "build.py")
    try:
        # build.py 실행 (--publish 플래그 포함)
        res = subprocess.run(
            [sys.executable, build_script, "--data", FINAL_PATH, "--publish"],
            capture_output=True, text=True, check=True
        )
        print("✓ [배포 완료] 빌드 및 퍼블리싱 성공!")
        print(res.stdout)
        send_telegram(f"📢 [배포 완료] 오늘의 IT/AI 뉴스 배포가 성공적으로 완료되었습니다!\n날짜: {datetime.now().strftime('%Y-%m-%d')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ [배포 실패] build.py 실행 에러: {e}")
        print(e.stderr)
        send_telegram(f"🚨 [배포 실패] 빌드/퍼블리싱 과정에서 오류가 발생했습니다.\n에러: {e.stderr[:300]}")
        return False

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"=== 14:00 배포 관리 및 폴백 시스템 기동 ({today_str}) ===")
    
    draft_valid = False
    
    # 1. 초안 파일 확인
    if os.path.exists(DRAFT_PATH):
        try:
            with open(DRAFT_PATH, "r", encoding="utf-8") as f:
                draft_data = json.load(f)
            
            draft_date = draft_data.get("date", "")
            if draft_date == today_str:
                # 오늘 자 초안이 맞고 유효함
                draft_valid = True
                print("✓ 오늘 날짜의 뉴스 초안(draft)이 정상적으로 존재합니다.")
            else:
                print(f"⚠ 초안 날짜 불일치 (오늘: {today_str}, 초안: {draft_date})")
        except Exception as e:
            print(f"✗ 초안 파일 읽기 오류: {e}")
    else:
        print("⚠ 초안 파일이 존재하지 않습니다.")

    # 2. 초안이 유효한 경우 최종 news_data.json 복사 후 배포
    if draft_valid:
        try:
            with open(DRAFT_PATH, "r", encoding="utf-8") as f_in:
                draft_content = f_in.read()
            with open(FINAL_PATH, "w", encoding="utf-8") as f_out:
                f_out.write(draft_content)
            print("✓ 초안(draft)을 최종 news_data.json으로 인수인계 완료.")
            
            run_build_and_publish()
        except Exception as e:
            print(f"✗ news_data.json 복사 실패: {e}")
            send_telegram(f"🚨 [배포 오류] 초안 인수인계 중 예외가 발생했습니다: {e}")
    
    # 3. 초안이 없거나 날짜가 맞지 않는 경우 -> 배포 중단 및 경고 알림
    else:
        print("🚨 [배포 중단] 오늘 날짜의 유효한 초안(draft)이 존재하지 않아 배포를 진행하지 못했습니다.")
        send_telegram(f"🚨 [배포 중단] {today_str} 자 뉴스 초안(draft)이 없거나 유효하지 않습니다. 안티그래비티 2.0 기동 또는 수동 확인이 필요합니다.")

if __name__ == "__main__":
    main()

# Checkpoint 21 - Daily Automation Approval Request Fix

## 1. 현재 완료 상태

- 14:00 `daily-news-generation` 자동화가 `03_card_brief.md` 부재 시 즉시 중단되는 문제를 수정했다.
- 자동화 프롬프트를 다음 흐름으로 변경했다.
  - 오늘 `daily_news/YYYY-MM-DD/` 생성
  - `01_news_pool.md`, `02_fact_check.md`, `03_card_brief.md`가 없으면 최근 24시간 뉴스 조사 후 생성
  - `scripts/pipeline_v3.py` 실행
  - `scripts/telegram_approval_gate.py --init --send --require-send` 실행
  - Instagram, Threads, Google Drive, Blog 업로드는 수행하지 않음
- `telegram_approval_gate.py`가 환경변수 또는 macOS Keychain에서 Telegram 인증정보를 읽도록 보강했다.
- `--require-send` 옵션을 추가하여 Telegram 발송 실패를 조용히 성공 처리하지 않도록 했다.
- Python 문법 검사는 통과했다.

## 2. 결정된 규칙

- 14:00 자동화는 단순 입력 파일 대기 방식이 아니라, 필요한 일일 브리핑 입력 파일을 직접 생성해야 한다.
- Telegram 승인 요청은 실제 발송을 시도해야 한다.
- Telegram 발송 실패 시 실패 원인을 상태 파일에 남기고 게시 단계로 넘어가지 않는다.
- 게시 업로드는 승인 후 별도 publish flow에서만 수행한다.

## 3. 폐기된 선택지

- `03_card_brief.md`가 없으면 자동화가 바로 중단되는 방식은 폐기한다.
- Telegram 승인 메시지를 파일로만 만들고 실제 발송하지 않는 기본 흐름은 폐기한다.
- Telegram 전송 실패를 단순 dry-run 성공처럼 처리하는 방식은 폐기한다.

## 4. 다음 단계 입력값

- 활성 자동화:
  - `/Users/seongjegeun/.codex/automations/daily-news-generation/automation.toml`
  - `/Users/seongjegeun/.codex/automations/metrics-collection/automation.toml`
- Telegram 인증정보 현재 확인 결과:
  - `TELEGRAM_BOT_TOKEN`: 자동화 환경/Keychain에서 미확인
  - `TELEGRAM_CHAT_ID`: 자동화 환경/Keychain에서 미확인
- Keychain service names:
  - `media-os-telegram-bot-token`
  - `media-os-telegram-chat-id`

## 5. 반드시 유지해야 할 정책

- 토큰 원문을 일반 파일, 로그, 보고서에 저장하지 않는다.
- `::inbox-item` 출력 금지.
- 승인 없는 게시 금지.
- Telegram 승인 요청 실패 시 Instagram/Threads 게시 금지.

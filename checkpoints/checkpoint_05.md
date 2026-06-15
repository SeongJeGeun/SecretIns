# checkpoint_05

작성일: 2026-06-02

## 1. 현재 완료 상태

- Telegram 실제 수신 대상 `chat_id=6219612697`로 `sendMessage` 테스트를 완료했다.
- Telegram API 응답 기준 HTTP 200, `ok=true`를 확인했다.
- Google Drive Refresh Token 생성을 위한 OAuth 인증 URL을 생성했다.
- Google Drive Scope는 `https://www.googleapis.com/auth/drive.file`로 고정했다.
- Authorization Code는 아직 수신되지 않아 Refresh Token 교환과 Drive 업로드 테스트는 진행하지 않았다.

## 2. 결정된 규칙

- Telegram 전송에는 Bot ID가 아니라 실제 수신자 chat_id를 사용한다.
- Google Drive 업로드 자동화에는 Refresh Token 또는 Access Token이 필요하다.
- Client ID와 Client Secret만으로는 Drive 업로드를 수행하지 않는다.
- Refresh Token 교환은 사용자가 Google 로그인 승인 후 받은 Authorization Code를 제공한 뒤 진행한다.
- 토큰 원문은 파일과 보고서에 저장하지 않는다.

## 3. 폐기된 선택지

- Bot ID를 Telegram chat_id로 사용하는 방식은 폐기한다.
- Authorization Code 없이 Refresh Token을 생성하려는 방식은 폐기한다.
- Google Drive API 활성화 여부와 OAuth Consent Screen 상태를 추측으로 판단하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_05.md`
- `daily_news/2026-06-02/output/google_drive_refresh_token_generator/refresh_token_generation_report.md`
- `daily_news/2026-06-02/output/google_drive_refresh_token_generator/google_oauth_status.json`

필요 입력값:

- Google OAuth 승인 후 받은 Authorization Code
- 또는 승인 후 리다이렉트된 전체 URL

## 5. 반드시 유지해야 할 정책

- 토큰 원문은 출력하지 않는다.
- 토큰 원문은 파일에 저장하지 않는다.
- Google API 상태는 실제 HTTP 응답 기준으로만 판단한다.
- Instagram 업로드는 Google Drive 공개 이미지 URL 확보 후에만 진행한다.
- 주요 단계 종료 시 checkpoint를 생성한다.

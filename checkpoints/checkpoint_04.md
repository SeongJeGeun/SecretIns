# checkpoint_04

작성일: 2026-06-02

## 1. 현재 완료 상태

- `SOCIAL_PUBLISHING_FIX_V1` 재검증을 완료했다.
- 기존 실패 보고서는 `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/archive/experiments/publishing_failed_report_2026-06-02`로 이동해 폐기/보관 처리했다.
- Telegram은 `getUpdates`를 사용하지 않고 직접 `sendMessage`를 호출했다.
- Google Drive는 제공 OAuth 앱 정보만으로 업로드 토큰을 받을 수 있는지 실제 토큰 엔드포인트로 확인했다.
- Instagram 계정 읽기 검증은 성공했지만, Drive 공개 URL이 없어 캐러셀 게시를 시작하지 않았다.
- Threads 텍스트 게시와 게시 확인은 성공했다.
- 새 결과 보고서는 `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-02/output/publishing_test_fix/publish_report_v2.md`에 저장했다.

## 2. 결정된 규칙

- Telegram 보고에는 Bot ID가 아닌 실제 수신 대상 `chat_id`가 필요하다.
- Google Drive 업로드에는 OAuth client id/client secret 외에 사용자 권한이 부여된 access token 또는 refresh token이 필요하다.
- Instagram에는 로컬 PNG를 사용하지 않고, 공개 접근 가능한 HTTPS 이미지 URL만 사용한다.
- 공개 URL이 준비되지 않으면 Instagram media container를 생성하지 않는다.
- Threads는 Instagram과 별도 채널이며 텍스트 전용 게시가 가능하다.

## 3. 폐기된 선택지

- Bot ID `8687471727`을 Telegram 수신 chat_id로 사용하는 선택지는 API 응답 기준으로 폐기한다.
- OAuth client id/client secret만으로 Google Drive 업로드를 진행하는 선택지는 API 응답 기준으로 폐기한다.
- Drive 공개 URL 없이 Instagram 캐러셀 컨테이너를 생성하는 선택지는 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_04.md`
- `daily_news/2026-06-02/output/publishing_test_fix/publish_report_v2.md`
- `daily_news/2026-06-02/output/publishing_test_fix/error_log_v2.json`

필요 입력값:

- Telegram 실제 수신 대상 chat_id
- Google Drive 업로드 가능한 OAuth access token 또는 refresh token
- 또는 PNG 10장의 이미 검증된 공개 HTTPS URL 목록

## 5. 반드시 유지해야 할 정책

- 토큰 원문은 파일과 로그에 저장하지 않는다.
- Instagram과 Threads는 별도 채널로 취급한다.
- Threads에는 카드뉴스 이미지를 업로드하지 않는다.
- Instagram은 Google Drive 공개 URL 또는 동등한 공개 HTTPS URL 확보 후에만 게시한다.
- 주요 단계 종료 시 다음 checkpoint를 생성한다.

# checkpoint_03

작성일: 2026-06-02

## 1. 현재 완료 상태

- `SOCIAL_PUBLISHING_TEST_V1` 실제 게시 작업을 시도했다.
- 입력 카드뉴스 PNG 10장은 확인했다.
- Instagram 게시 전 필수 조건인 공개 HTTPS `image_url` 목록이 없음을 확인했다.
- Instagram Graph API 미디어 컨테이너 생성 전 단계에서 중단했다.
- Threads는 Instagram 실패 시 업로드 중단 규칙에 따라 게시하지 않았다.
- Telegram 보고는 시도 조건을 확인했으나 `getUpdates`에서 보고 대상 `chat_id`를 찾지 못해 발송하지 못했다.
- 게시 실패/중단 보고서는 `daily_news/2026-06-02/output/publishing_test/publish_report.md`에 저장했다.
- 오류 로그는 `daily_news/2026-06-02/output/publishing_test/error_log.json`에 저장했다.

## 2. 결정된 규칙

- Instagram 캐러셀 게시에는 각 PNG별 공개 접근 가능한 HTTPS 이미지 URL이 필요하다.
- 로컬 PNG 파일 경로는 Instagram Graph API의 `image_url`로 사용할 수 없다.
- 공개 URL이 없으면 미디어 컨테이너 생성도 하지 않는다.
- Instagram 실패 시 Threads 게시를 진행하지 않는다.
- Telegram 보고를 자동화하려면 Bot과 대화한 `chat_id`가 필요하다.

## 3. 폐기된 선택지

- 로컬 파일 경로를 `image_url`로 넣어 Instagram media container 생성을 시도하는 선택지는 폐기했다.
- 공개 호스팅 없이 외부 임시 업로드 서비스를 임의 사용하는 선택지는 폐기했다.
- Instagram 실패 상태에서 Threads만 단독 게시하는 선택지는 현재 workflow 규칙상 폐기했다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_03.md`
- `daily_news/2026-06-02/output/publishing_test/publish_report.md`
- `daily_news/2026-06-02/output/publishing_test/error_log.json`

필요 입력값:

- Instagram 업로드용 카드 PNG 10장의 공개 HTTPS URL 목록
- 또는 프로젝트 내부에서 사용할 공식 이미지 호스팅 방식
- Telegram 보고 대상 `chat_id` 또는 사용자가 먼저 Bot에게 메시지를 보낸 상태

권장 URL 목록 파일:

- `daily_news/2026-06-02/output/publishing_test/public_image_urls.json`

## 5. 반드시 유지해야 할 정책

- 토큰 원문은 파일과 로그에 저장하지 않는다.
- 게시/업로드 API 호출은 사용자가 명시한 작업 범위 안에서만 수행한다.
- Instagram과 Threads는 별도 채널로 취급한다.
- Threads에는 카드뉴스 이미지를 업로드하지 않는다.
- Instagram 게시 성공 전에는 현재 workflow에서 Threads 게시를 진행하지 않는다.
- 다음 주요 단계 종료 시 `checkpoint_04.md`를 생성한다.

# checkpoint_07

작성일: 2026-06-02

## 1. 현재 완료 상태

- Google OAuth Authorization Code를 Refresh Token과 Access Token으로 교환했다.
- Token API 응답 기준 HTTP 200을 확인했다.
- Google Drive 업로드 테스트를 완료했다.
- 테스트 PNG `instagram_url_test_2026-06-02_daily-news_01.png`를 Drive에 업로드했다.
- Drive 파일에 `anyone reader` 공개 권한을 설정했다.
- 공개 다운로드 URL의 비인증 접근을 확인했다.
- Instagram Graph API가 해당 공개 이미지 URL을 처리할 수 있는지 확인했다.
- Instagram 게시물 publish는 수행하지 않았다.

## 2. 결정된 규칙

- Google Drive 업로드에는 `.secrets/google_drive_refresh_token.txt`에 저장된 Refresh Token을 사용한다.
- Refresh Token 원문은 보고서와 일반 로그에 기록하지 않는다.
- Instagram 카드뉴스 업로드에는 Drive 공개 다운로드 URL을 사용한다.
- Instagram Graph API URL 검증은 media container 생성까지 허용하되, publish는 별도 명시 작업에서만 수행한다.
- 공개 URL은 비인증 GET에서 HTTP 200과 `image/png` 응답을 확인한 것만 사용한다.

## 3. 폐기된 선택지

- Authorization Code를 매번 다시 요구하는 방식은 폐기한다.
- 로컬 PNG 경로를 Instagram API에 직접 전달하는 방식은 폐기한다.
- 공개 접근 검증 없는 Drive URL을 Instagram 업로드에 사용하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_07.md`
- `daily_news/2026-06-02/output/google_drive_refresh_token_generator/authorization_exchange_report.md`
- `daily_news/2026-06-02/output/google_drive_refresh_token_generator/authorization_exchange_result.json`

검증된 테스트 결과:

- Drive File ID: `1oggRhI43FNjenJdVf62hKHbrheBPSHQP`
- Public URL: `https://drive.google.com/uc?export=download&id=1oggRhI43FNjenJdVf62hKHbrheBPSHQP`
- Instagram Container ID: `18080256101214492`
- Published: false

## 5. 반드시 유지해야 할 정책

- 토큰 원문은 출력하지 않는다.
- 토큰 원문은 일반 보고서에 저장하지 않는다.
- Google Drive 공개 URL은 실제 접근 가능 여부를 검증한 뒤 사용한다.
- Instagram 게시물 publish는 사용자가 명시적으로 요청한 경우에만 실행한다.
- 주요 단계 종료 시 checkpoint를 생성한다.

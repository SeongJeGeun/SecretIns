# checkpoint_08

작성일: 2026-06-02

## 1. 현재 완료 상태

- Instagram 최신 게시물을 Graph API로 조회했다.
- 최신 게시물의 Post ID, Permalink, Media Type, Published Time을 확인했다.
- Carousel children 기준 Media Count 10장을 확인했다.
- Telegram 보고 테스트를 완료했다.
- Telegram API 응답 기준 HTTP 200과 Message ID 218을 확인했다.

## 2. 결정된 규칙

- Instagram 게시 성공 여부는 Graph API 최신 media 조회와 permalink 존재 여부로 재검증한다.
- Carousel Media Count는 `children.data` 개수로 판단한다.
- Telegram 보고 성공 여부는 `sendMessage` HTTP 200과 `ok=true` 기준으로 판단한다.
- API 토큰 원문은 보고서와 로그에 저장하지 않는다.

## 3. 폐기된 선택지

- 이전 publish 단계의 403 응답만으로 최종 실패로 확정하는 방식은 폐기한다.
- Instagram 앱 화면 확인 없이 추측으로 URL을 만드는 방식은 폐기한다.
- Telegram Message ID 없이 보고 성공으로 처리하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_08.md`
- `daily_news/2026-06-02/output/instagram_post_validation/instagram_post_validation_report.md`
- `daily_news/2026-06-02/output/instagram_post_validation/instagram_post_validation_result.json`

확인된 게시 결과:

- Instagram Post ID: `18100227307894992`
- Instagram URL: `https://www.instagram.com/p/DZFUw1QCbEc/`
- Media Count: 10
- Published Time: `2026-06-02T12:17:22+0000`
- Telegram Message ID: `218`

## 5. 반드시 유지해야 할 정책

- 토큰 원문은 출력하지 않는다.
- 토큰 원문은 파일에 저장하지 않는다.
- 게시 성공 여부는 실제 API 응답으로만 판단한다.
- 주요 단계 종료 시 checkpoint를 생성한다.

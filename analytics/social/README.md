# Social Analytics System

현재 목적은 Instagram + Threads 성과 수집 구조를 운영 가능한 상태로 준비하는 것이다. 이 폴더의 코드는 자동 실행되지 않으며, 수집 시점에 운영자가 직접 실행한다.

## 생성 파일

- `social_metrics.xlsx`: 성과 기록용 엑셀 원본
- `collect_social_metrics.py`: Instagram / Threads 읽기 전용 지표 수집 코드
- `api_field_mapping.md`: 플랫폼별 수집 가능 필드와 엔드포인트
- `google_docs_report_template.md`: Google Docs로 옮겨 쓸 보고서 템플릿

## 실행 전 환경변수

토큰은 파일에 저장하지 않는다. 실행 세션에서만 환경변수로 주입한다.

```bash
export INSTAGRAM_ACCESS_TOKEN="..."
export INSTAGRAM_IG_USER_ID="..."
export THREADS_ACCESS_TOKEN="..."
export THREADS_USER_ID="..."
export SOCIAL_METRICS_XLSX="/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/analytics/social/social_metrics.xlsx"
```

## 수동 실행 예시

Instagram 게시물 1건 수집:

```bash
python3 collect_social_metrics.py \
  --workbook "$SOCIAL_METRICS_XLSX" \
  --instagram-media-id "INSTAGRAM_MEDIA_ID" \
  --campaign "daily_news_2026-06-02" \
  --content-type "carousel"
```

Threads 게시물 1건 수집:

```bash
python3 collect_social_metrics.py \
  --workbook "$SOCIAL_METRICS_XLSX" \
  --threads-post-id "THREADS_POST_ID" \
  --campaign "daily_news_2026-06-02" \
  --content-type "text"
```

## 운영 원칙

- 읽기 API만 사용한다.
- 게시, 수정, 삭제, 댓글, DM, 계정 변경 API는 사용하지 않는다.
- 토큰 원문을 출력하거나 저장하지 않는다.
- Instagram `followers_gained`는 게시물 단일 API 지표가 아니라 계정 팔로워 수의 전후 차이로 계산한다.
- Threads `shares`는 API 응답 가능 여부를 실제 응답으로 확인해 기록한다. 미제공이면 빈 값으로 둔다.
- Threads 성과 분석 단위는 종합 요약 게시물 1개가 아니라 **뉴스 카드 1개당 Threads 게시물 1개**다.
- Threads 게시물은 150~300자, 핵심 사실 / 배경 설명 / 질문 1개 구조로 기록한다.

## Threads 게시 로직

`scripts/publish_threads_per_card.py`는 `03_card_brief.md`에서 커버와 CTA를 제외한 뉴스 카드만 읽어 Threads 초안을 생성한다.

기본 실행은 dry-run이며 실제 게시하지 않는다.

```bash
/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/scripts/publish_threads_per_card.py \
  --brief /Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-02/03_card_brief.md \
  --output-dir /Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-02/output/threads_policy_v2
```

실제 게시가 필요한 경우에만 `--execute`를 붙인다.

```bash
THREADS_ACCESS_TOKEN="..." THREADS_USER_ID="..." \
/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/scripts/publish_threads_per_card.py \
  --brief /Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-02/03_card_brief.md \
  --output-dir /Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-02/output/threads_policy_v2 \
  --execute
```

## 자동화 준비 상태

현재 구조는 수동 실행 준비 상태다. 자동화가 필요할 경우 별도 스케줄러에서 이 스크립트를 호출하면 된다. 자동 실행 등록은 아직 하지 않는다.

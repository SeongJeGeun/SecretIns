# checkpoint_09

작성일: 2026-06-02

## 1. 현재 완료 상태

- Instagram + Threads 성과 수집 시스템을 `analytics/social/` 하위에 구축했다.
- `social_metrics.xlsx`를 생성했고 다음 시트를 포함했다.
  - `instagram_posts`
  - `threads_posts`
  - `daily_summary`
  - `content_analysis`
  - `3day_report`
- 각 시트에 샘플 데이터 1건과 기본 계산 컬럼을 삽입했다.
- Instagram / Threads 읽기 전용 수집 코드 `collect_social_metrics.py`를 작성했다.
- Google Docs로 옮겨 쓸 수 있는 성과 보고서 템플릿을 작성했다.
- 코드가 수집 대상 ID 없이 실행될 때 API 호출 없이 종료되는 것을 확인했다.
- 이번 산출물과 체크포인트 영역에서 원문 토큰 조각이 저장되지 않았음을 확인했다.

## 2. 결정된 규칙

- 소셜 성과 분석 산출물 표준 위치는 `PROJECT_ROOT/analytics/social/`이다.
- 수집 코드는 자동 실행하지 않는다.
- 토큰은 환경변수에서만 읽고, 파일에 저장하지 않는다.
- Instagram `followers_gained`는 게시물 단일 지표가 아니라 계정 `followers_count` 전후 차이로 계산한다.
- Threads는 `THREADS_POLICY_V2`에 따라 뉴스 카드 1개당 Threads 게시물 1개를 기본 분석 단위로 본다.
- 분석 지표는 좋아요보다 저장, 댓글, 답글, 재공유, 인용 등 체류와 대화 신호를 더 중시한다.

## 3. 폐기된 선택지

- 토큰을 코드나 설정 파일에 직접 저장하는 방식은 폐기한다.
- 전체 뉴스 요약 Threads 게시물 1개를 단일 성과 단위로 보는 방식은 폐기한다.
- 자동 스케줄러를 즉시 등록하는 방식은 폐기한다.
- Instagram 팔로워 증가를 게시물 API 단일 응답에서 직접 수집한다고 가정하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_09.md`
- `analytics/social/README.md`
- `analytics/social/api_field_mapping.md`
- `analytics/social/social_metrics.xlsx`

필요 환경변수:

- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_IG_USER_ID`
- `THREADS_ACCESS_TOKEN`
- `THREADS_USER_ID`
- `SOCIAL_METRICS_XLSX`

## 5. 반드시 유지해야 할 정책

- 모든 최종 산출물은 `PROJECT_ROOT` 내부에만 저장한다.
- 실제 데이터 수집은 운영자가 명시적으로 지시할 때만 수행한다.
- API 토큰 원문은 출력하거나 저장하지 않는다.
- 게시, 수정, 삭제, 댓글, DM, 계정 변경 API는 분석 수집 코드에 포함하지 않는다.
- 실패 응답을 저장할 때도 토큰 파라미터는 마스킹한다.

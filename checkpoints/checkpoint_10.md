# checkpoint_10

작성일: 2026-06-02

## 1. 현재 완료 상태

- `THREADS_POLICY_IMPLEMENTATION_V1`을 현재 운영 로직에 반영했다.
- 기존 `뉴스 전체 = Threads 1개` 방식은 폐기했다.
- 새 `뉴스 카드 1개 = Threads 게시물 1개` 방식으로 `scripts/publish_threads_per_card.py`를 추가했다.
- 현재 `daily_news/2026-06-02/03_card_brief.md` 기준 뉴스 카드 8개를 추출했다.
- Threads 초안 8개를 생성했다.
- 8개 초안 모두 150~300자, 질문 1개 기준을 통과했다.
- 실제 Threads 게시 API는 호출하지 않았다.
- 원문 토큰 조각이 새 산출물에 저장되지 않았음을 확인했다.

## 2. 결정된 규칙

- Threads는 Instagram 캡션을 복사하지 않는다.
- Threads는 카드뉴스 이미지를 업로드하지 않는다.
- 일일 뉴스 Threads는 종합 요약 게시물 1개가 아니라 뉴스 카드별 게시물 N개로 운영한다.
- 각 Threads 게시물은 다음 구조를 따른다.
  1. 뉴스 핵심 사실
  2. 배경 설명
  3. 질문 1개
- 게시물 길이는 150~300자를 기준으로 한다.
- 중립 유지, 정치 편향 금지, 선동 금지, 투자 권유 금지를 유지한다.
- 실제 게시는 `--execute`가 명시된 경우에만 수행한다.

## 3. 폐기된 선택지

- "오늘의 뉴스 브리핑" 같은 종합 요약형 Threads 게시물 1개 방식은 폐기한다.
- Instagram 게시문을 Threads에 그대로 복사하는 방식은 폐기한다.
- 카드뉴스 이미지를 Threads에 업로드하는 방식은 폐기한다.
- 질문 없이 사실만 나열하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_10.md`
- `scripts/publish_threads_per_card.py`
- `daily_news/2026-06-02/output/threads_policy_v2/threads_policy_v2_drafts.md`
- `daily_news/2026-06-02/output/threads_policy_v2/implementation_report.md`

현재 생성된 Threads 초안 수:

- 8개

## 5. 반드시 유지해야 할 정책

- 모든 산출물은 `PROJECT_ROOT` 내부에 저장한다.
- 토큰 원문은 출력하거나 파일에 저장하지 않는다.
- 실제 게시 API 호출은 명시적 게시 지시가 있을 때만 수행한다.
- Threads는 뉴스 카드 1개당 게시물 1개로 작성한다.

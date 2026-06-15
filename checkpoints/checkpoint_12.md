# checkpoint_12

작성일: 2026-06-02

## 1. 현재 완료 상태

- `PIPELINE_V3_IMPLEMENTATION`을 구축했다.
- V2는 보존하고 V3 전용 스크립트 `scripts/pipeline_v3.py`를 추가했다.
- V3 스키마 `pipeline/news_dataset.v3.schema.json`을 추가했다.
- V3 운영 문서 `pipeline/PIPELINE_V3.md`를 추가했다.
- `pipeline/README.md`와 `memory/active_memory.md`를 V3 기준으로 갱신했다.
- 현재 `daily_news/2026-06-02/03_card_brief.md` 기준으로 V3 `news_dataset.json`을 생성했다.
- V3 병렬 Agent dry-run을 실행했다.
  - Instagram Agent: ready
  - Threads Agent: ready
  - Telegram Agent: ready
  - Blog Agent: ready
  - Analytics Agent: ready
- `pipeline_result.json`과 `pipeline_result.md`를 생성했다.
- 실제 게시 API와 업로드 API는 호출하지 않았다.
- 새 산출물에 원문 토큰 조각이 저장되지 않았음을 확인했다.

## 2. 결정된 규칙

- 현재 운영 표준 파이프라인은 `PIPELINE_V3_IMPLEMENTATION`이다.
- `news_dataset.json`은 단일 Source of Truth다.
- V3 `news_dataset`의 각 뉴스 항목은 다음 필드를 포함한다.
  - `id`
  - `category`
  - `importance`
  - `headline`
  - `summary`
  - `source`
  - `instagram`
  - `threads`
  - `blog`
  - `analytics`
- 각 채널 Agent는 서로 의존하지 않고 `news_dataset.json`만 참조한다.
- Threads는 뉴스 1개당 게시물 1개를 생성한다.
- 종합 브리핑 Threads는 금지한다.
- Publish Gate는 `not_executed`, `draft`, `approved`, `published` 4단계를 지원한다.

## 3. 폐기된 선택지

- Agent가 각자 다른 원본 파일에서 초안을 생성하는 방식은 폐기한다.
- V2처럼 Agent 단계에서 채널별 초안을 처음 만드는 방식은 V3 운영 표준에서는 폐기한다.
- 종합 브리핑 Threads 1개 방식은 폐기한다.
- 기본 파이프라인 실행에서 게시 또는 업로드 API를 호출하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_12.md`
- `scripts/pipeline_v3.py`
- `pipeline/PIPELINE_V3.md`
- `daily_news/2026-06-02/pipeline_v3/news_dataset.json`
- `daily_news/2026-06-02/pipeline_v3/pipeline_result.md`

현재 dry-run 결과:

- News Count: 8
- Aggregate Status: ready
- Publish Status: not_executed
- Live API Calls: False

## 5. 반드시 유지해야 할 정책

- 모든 산출물은 `PROJECT_ROOT` 내부에 저장한다.
- 토큰 원문은 출력하거나 파일에 저장하지 않는다.
- 실제 게시 API와 업로드 API는 명시적 라이브 게시 지시가 있을 때만 호출한다.
- Threads는 뉴스 1개당 게시물 1개로 작성한다.
- 모든 Agent는 `news_dataset.json`만 공통 입력으로 사용한다.

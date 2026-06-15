# checkpoint_11

작성일: 2026-06-02

## 1. 현재 완료 상태

- `PIPELINE_REFACTOR_V2` 구조를 구축했다.
- `scripts/pipeline_v2.py`를 생성했다.
- `pipeline/README.md`와 `pipeline/news_dataset.schema.json`을 생성했다.
- 현재 `daily_news/2026-06-02/03_card_brief.md` 기준으로 `news_dataset.json`을 생성했다.
- 5개 Agent를 병렬 실행하는 dry-run을 완료했다.
  - Instagram Agent
  - Threads Agent
  - Telegram Agent
  - Blog Agent
  - Analytics Agent
- Agent 결과를 `pipeline_result.json`과 `pipeline_result.md`로 취합했다.
- 실제 게시 API는 호출하지 않았다.
- 새 산출물에 원문 토큰 조각이 저장되지 않았음을 확인했다.

## 2. 결정된 규칙

- 일일 뉴스 제작은 `news_dataset.json`을 단일 입력으로 사용한다.
- 모든 Agent는 같은 `news_dataset.json`을 읽고 병렬 실행된다.
- Threads Agent는 `THREADS_POLICY_V2`를 적용해 뉴스 카드 1개당 Threads 게시물 1개를 생성한다.
- 기본 실행은 dry-run이다.
- 게시 단계는 결과 취합 후 별도 게시 게이트를 통과해야 한다.
- 파이프라인 결과에는 토큰 원문을 저장하지 않는다.

## 3. 폐기된 선택지

- 각 채널이 서로 다른 원본 파일을 읽어 따로 판단하는 방식은 폐기한다.
- Instagram 작업 완료 후 Threads를 단순 복사하는 방식은 폐기한다.
- 종합 뉴스 요약 Threads 게시물 1개 방식은 폐기한다.
- 기본 파이프라인 실행에서 곧바로 게시 API를 호출하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_11.md`
- `scripts/pipeline_v2.py`
- `pipeline/README.md`
- `daily_news/2026-06-02/pipeline_v2/news_dataset.json`
- `daily_news/2026-06-02/pipeline_v2/pipeline_result.md`

현재 dry-run 결과:

- News Count: 8
- Aggregate Status: ready
- Publish Status: not_executed

## 5. 반드시 유지해야 할 정책

- 모든 산출물은 `PROJECT_ROOT` 내부에 저장한다.
- 토큰 원문은 출력하거나 파일에 저장하지 않는다.
- 실제 게시 API는 명시적 게시 지시가 있을 때만 호출한다.
- Threads는 뉴스 카드 1개당 게시물 1개로 작성한다.
- Agent 공통 입력은 `news_dataset.json`으로 통일한다.

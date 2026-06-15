# checkpoint_16

작성일: 2026-06-02

## 1. 현재 완료 상태

- `SCHEDULER_REGISTRATION_V1`을 수행했다.
- Codex Automations 4개를 실제 등록했다.
  - Daily News Generation
  - Approval Watcher
  - Metrics Collection
  - 3 Day Analysis
- 각 자동화 카드를 확인했다.
- 등록 결과를 `pipeline/scheduler_registration_report.md`에 기록했다.

## 2. 결정된 규칙

- Daily News Generation은 매일 14:00 실행한다.
- Approval Watcher는 15분 간격으로 승인 상태를 확인한다.
- Metrics Collection은 매일 18:00 실행한다.
- 3 Day Analysis는 3일마다 20:00 실행한다.
- 모든 게시/업로드 작업은 `publish_ledger.json`과 `publish_status == approved` 조건을 통과해야 한다.

## 3. 폐기된 선택지

- `SYSTEM_READY` 이전 Scheduler 등록 보류 상태는 종료했다.
- 승인 없는 게시 경로는 계속 폐기한다.
- ledger 없는 중복 게시 가능 경로는 계속 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_16.md`
- `pipeline/scheduler_registration_report.md`
- `pipeline/scheduler_plan_v1.md`
- `pipeline/system_ready_audit/system_ready_audit.md`

Automation ID:

- `daily-news-generation`
- `approval-watcher`
- `metrics-collection`
- `3-day-analysis`

## 5. 반드시 유지해야 할 정책

- 토큰 원문은 출력하거나 파일에 저장하지 않는다.
- 게시 Worker는 `publish_status=approved`일 때만 실행한다.
- `publish_ledger.json`으로 중복 게시를 방지한다.
- 초기 7일 Telegram 승인 게이트를 유지한다.

# Checkpoint 20 - Inbox Item Output Disabled

## 1. 현재 완료 상태

- 활성 Codex Automations 2개에 inbox item 출력 금지 규칙을 반영했다.
- 대상:
  - `/Users/seongjegeun/.codex/automations/daily-news-generation/automation.toml`
  - `/Users/seongjegeun/.codex/automations/metrics-collection/automation.toml`
- 두 자동화 모두 다음 규칙을 포함한다.
  - `Do not emit inbox items.`
  - `Never output ::inbox-item blocks.`
  - `Report only in plain text or write only to the status file.`

## 2. 결정된 규칙

- Codex Automation은 `::inbox-item` 블록을 출력하지 않는다.
- 자동화 결과는 plain text 보고 또는 상태 파일 기록으로만 남긴다.
- 알림성 UI 블록 생성을 유도하는 출력 형식은 사용하지 않는다.

## 3. 폐기된 선택지

- Automation 결과에 inbox item 블록을 포함하는 방식은 폐기한다.
- 반복 알림을 만들 수 있는 status report 출력 형식은 사용하지 않는다.

## 4. 다음 단계 입력값

- 활성 자동화:
  - `daily-news-generation`: 매일 14:00
  - `metrics-collection`: 매일 18:00
- 비활성 자동화:
  - `approval-watcher`
  - `3-day-analysis`

## 5. 반드시 유지해야 할 정책

- 승인 없는 게시 금지.
- 실제 API 호출은 명시된 운영 절차 없이 수행하지 않는다.
- 토큰 원문은 출력하거나 일반 파일에 저장하지 않는다.
- 자동화 출력은 plain text 또는 status file만 허용한다.

# checkpoint_13

작성일: 2026-06-02

## 1. 현재 완료 상태

- `TELEGRAM_APPROVAL_GATE_V1`을 구현했다.
- `scripts/telegram_approval_gate.py`를 추가했다.
- `pipeline/TELEGRAM_APPROVAL_GATE.md`를 추가했다.
- `pipeline/scheduler_plan_v1.md`를 추가했다.
- `scripts/approval_7day_report.py`를 추가했다.
- `pipeline/PIPELINE_V3.md`와 `memory/active_memory.md`에 Telegram 승인 게이트 정책을 반영했다.
- 현재 `daily_news/2026-06-02/pipeline_v3/news_dataset.json`의 `publish_status`를 `draft`로 설정했다.
- `daily_news/2026-06-02/approval_gate/`에 승인 상태 파일과 승인 메시지 파일을 생성했다.
- APPROVE / REJECT / Timeout 분기를 테스트 복사본으로 검증했다.
- 실제 Telegram 전송, 게시 API, 업로드 API는 호출하지 않았다.
- 새 산출물에 원문 토큰 조각이 저장되지 않았음을 확인했다.

## 2. 결정된 규칙

- 초기 운영 7일 동안 게시 전 Telegram 승인 절차를 강제한다.
- 매일 14:00 `pipeline_v3.py --publish-status draft`를 실행한다.
- 이후 `telegram_approval_gate.py --init`으로 승인 대기 상태를 만든다.
- `APPROVE` 수신 시 `publish_status=approved`로 전환한다.
- `REJECT` 수신 시 `publish_status=draft`를 유지하고 게시를 금지한다.
- 4시간 이내 응답이 없으면 timeout 처리하고 `publish_status=draft`를 유지한다.
- 게시 Worker는 `publish_status=approved`일 때만 실행할 수 있다.
- 7일 종료 후 `approval_7day_report.py`로 운영 리포트를 생성한다.

## 3. 폐기된 선택지

- 초기 7일 동안 자동 게시하는 방식은 폐기한다.
- 승인 응답 없이 timeout 후 자동 게시하는 방식은 폐기한다.
- Telegram 승인 메시지를 보내지 않고 게시 Worker가 바로 실행되는 방식은 폐기한다.
- 7일 종료 후 자동 승인으로 즉시 전환하는 방식은 폐기한다. 운영 리포트 기반 판단이 필요하다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_13.md`
- `scripts/telegram_approval_gate.py`
- `pipeline/TELEGRAM_APPROVAL_GATE.md`
- `pipeline/scheduler_plan_v1.md`
- `daily_news/2026-06-02/approval_gate/approval_state.json`
- `daily_news/2026-06-02/approval_gate/approval_message.md`

현재 상태:

- Approval Status: `waiting_approval`
- Publish Status: `draft`
- Live API Calls: `False`

## 5. 반드시 유지해야 할 정책

- 모든 산출물은 `PROJECT_ROOT` 내부에 저장한다.
- 토큰 원문은 출력하거나 파일에 저장하지 않는다.
- 실제 Telegram 전송은 `--send`가 있을 때만 수행한다.
- 실제 게시 API와 업로드 API는 명시적 라이브 게시 지시와 `publish_status=approved` 조건이 모두 충족될 때만 호출한다.
- 초기 7일 동안 승인 없는 자동 게시를 금지한다.

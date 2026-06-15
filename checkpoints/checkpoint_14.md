# checkpoint_14

작성일: 2026-06-02

## 1. 현재 완료 상태

- `SYSTEM_READY_AUDIT_V1`을 dry-run으로 수행했다.
- `scripts/system_ready_audit.py`를 생성했다.
- 감사 보고서를 생성했다.
  - `pipeline/system_ready_audit/system_ready_audit.json`
  - `pipeline/system_ready_audit/system_ready_audit.md`
- 실제 게시 API, 업로드 API, Telegram 전송 API는 호출하지 않았다.
- 최종 판정은 `FIX_REQUIRED`다.

## 2. 결정된 규칙

- Scheduler 등록 전에는 `SYSTEM_READY_AUDIT_V1`이 `READY`를 반환해야 한다.
- `publish_status=approved` 확인 없이 게시 가능한 경로는 허용하지 않는다.
- Instagram Publisher, Threads Publisher, Google Drive Uploader는 승인 게이트와 중복 게시 방지 장치를 가져야 한다.
- 초기 7일 동안 Telegram 승인 게이트를 우회할 수 없다.

## 3. 폐기된 선택지

- 현재 상태에서 Scheduler를 바로 등록하는 선택지는 폐기한다.
- 독립 Instagram Publisher 없이 과거 임시 게시 로그나 수동 스크립트에 의존하는 방식은 폐기한다.
- Google Drive Uploader 없이 업로드 준비가 완료된 것으로 판단하는 방식은 폐기한다.
- publish ledger 없이 중복 게시 방지가 된 것으로 판단하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_14.md`
- `pipeline/system_ready_audit/system_ready_audit.md`
- `scripts/system_ready_audit.py`

수정 필요 파일:

- `pipeline/.env.scheduler.example`
- `pipeline/scheduler_plan_v1.md`
- `scripts/google_drive_uploader.py`
- `scripts/instagram_publisher.py`
- `scripts/publish_threads_per_card.py`
- `status/publish_ledger.json`

## 5. 반드시 유지해야 할 정책

- 실제 API 호출 금지 지시가 있을 때는 dry-run만 수행한다.
- 토큰 원문은 출력하거나 파일에 저장하지 않는다.
- Scheduler 등록은 `READY` 판정 후에만 권장한다.
- 초기 7일 승인 게이트와 Threads 다중 게시 정책을 유지한다.

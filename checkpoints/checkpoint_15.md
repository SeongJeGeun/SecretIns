# checkpoint_15

작성일: 2026-06-02

## 1. 현재 완료 상태

- `SYSTEM_HARDENING_V1`을 구현했다.
- `publish_ledger.json`을 추가했다.
- 공통 게시 안전 가드 `scripts/publish_guard.py`를 추가했다.
- 독립 모듈을 추가했다.
  - `scripts/google_drive_uploader.py`
  - `scripts/instagram_publisher.py`
  - `scripts/threads_publisher.py`
- 기존 `scripts/publish_threads_per_card.py`도 `--execute` 시 `publish_status=approved`와 ledger를 확인하도록 보강했다.
- `pipeline/.env.scheduler.example`을 생성했다.
- `pipeline/scheduler_plan_v1.md`를 실제 명령 예시 기준으로 보강했다.
- `scripts/system_ready_audit.py`를 새 모듈 구조에 맞춰 갱신했다.
- 최종 감사 결과 `READY`를 확인했다.
- 실제 게시, 업로드, Telegram 전송, 외부 API 호출은 수행하지 않았다.

## 2. 결정된 규칙

- 모든 게시/업로드 모듈은 `publish_guard.preflight()`를 먼저 통과해야 한다.
- `publish_status != approved`이면 게시/업로드를 차단한다.
- `status/publish_ledger.json`에 같은 날짜와 채널이 이미 `published`이면 중복 실행을 차단한다.
- Google Drive, Instagram, Threads는 독립 모듈로 실행한다.
- 환경변수는 `pipeline/.env.scheduler.example`의 키를 기준으로 Scheduler에 주입한다.

## 3. 폐기된 선택지

- ledger 없이 게시하는 방식은 폐기한다.
- 승인 상태 확인 없이 Threads 게시로 진입하는 방식은 폐기한다.
- Instagram/Google Drive를 임시 과거 스크립트나 로그에 의존하는 방식은 폐기한다.
- 현재 dry-run 작업에서 실제 API를 호출하는 방식은 폐기한다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_15.md`
- `pipeline/system_hardening_report.md`
- `pipeline/system_ready_audit/system_ready_audit.md`
- `pipeline/scheduler_plan_v1.md`
- `scripts/publish_guard.py`

현재 최종 상태:

- System Audit: `READY`
- Current Publish Status: `draft`
- Publisher Dry-run Result: `blocked` because `publish_status_not_approved`
- Live API Calls: `False`

## 5. 반드시 유지해야 할 정책

- 실제 API 호출 금지 지시가 있으면 dry-run만 수행한다.
- 토큰 원문은 출력하거나 파일에 저장하지 않는다.
- Scheduler 등록 전 감사 결과가 `READY`인지 확인한다.
- 게시 Worker는 `publish_status=approved`일 때만 실행한다.
- 초기 7일 동안 Telegram 승인 게이트를 유지한다.

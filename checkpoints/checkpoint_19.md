# Checkpoint 19 - Stale Approval Gate Killed

## 1. 현재 완료 상태

- `media-os/daily_news/2026-06-02/approval_gate/` 활성 폴더를 제거했다.
- 해당 폴더는 `media-os/archive/publishing_tests/stale_approval_gate_2026-06-02_killed_20260603_023620/`로 이동했다.
- 활성 경로에는 `approval_gate_DISABLED.md`만 남겼다.
- `launchctl` 기준 승인 감시, 게시, Telegram, Instagram, Threads, pipeline 관련 등록 작업은 확인되지 않았다.
- 실행 중인 관련 자동화 프로세스도 확인되지 않았다.

## 2. 결정된 규칙

- 과거 날짜의 승인 게이트가 혼동을 만들면 활성 경로에서 제거하고 archive로 이동한다.
- `publish_status=approved`가 아닌 상태에서는 게시 경로를 열지 않는다.
- stale approval watcher report는 운영 중인 watcher로 간주하지 않는다.

## 3. 폐기된 선택지

- stale approval 상태 파일을 활성 경로에 계속 유지하는 방식은 폐기한다.
- 과거 `approval_watcher_status.md`를 현재 상태 보고로 재사용하지 않는다.
- 실제 API 호출로 상태를 재확인하는 방식은 사용하지 않았다.

## 4. 다음 단계 입력값

- 현재 활성 승인 게이트: 없음
- 현재 archive 위치: `media-os/archive/publishing_tests/stale_approval_gate_2026-06-02_killed_20260603_023620/`
- 활성 표시 파일: `media-os/daily_news/2026-06-02/approval_gate_DISABLED.md`

## 5. 반드시 유지해야 할 정책

- 실제 게시, 업로드, Telegram 전송은 명시적 운영 절차 없이 수행하지 않는다.
- 승인 없는 게시 금지.
- 중복 게시 방지 정책 유지.
- 토큰 원문은 로그나 보고서에 저장하지 않는다.

# checkpoint_17

작성일: 2026-06-02

## 1. 현재 완료 상태

- `PROJECT_CLEANUP_AUDIT_V1`을 수행했다.
- `media-os` 전체를 KEEP / ARCHIVE / DELETE_CANDIDATE로 분류했다.
- 실제 삭제와 실제 이동은 수행하지 않았다.
- 감사 보고서를 생성했다.
  - `pipeline/project_cleanup_audit/project_cleanup_audit.md`
  - `pipeline/project_cleanup_audit/project_cleanup_audit.json`

## 2. 결정된 규칙

- 현재 운영 핵심은 V3 파이프라인, Telegram 승인 게이트, publish ledger, publisher 모듈, analytics 시스템이다.
- 현재 일일 뉴스 최종 PNG와 assets는 KEEP으로 본다.
- `daily_news_test`, 과거 `daily_ai_news`, V2 pipeline 결과, approval gate test, 과거 publish test log는 ARCHIVE 후보로 본다.
- `node_modules`, `__pycache__`, `.DS_Store`, 테스트 샘플 PNG와 contact sheet는 DELETE_CANDIDATE로 본다.

## 3. 폐기된 선택지

- 감사 단계에서 실제 삭제하는 방식은 폐기했다.
- 감사 단계에서 실제 archive 이동하는 방식은 폐기했다.
- `.secrets`를 정리 후보로 보는 방식은 폐기했다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_17.md`
- `pipeline/project_cleanup_audit/project_cleanup_audit.md`
- `pipeline/project_cleanup_audit/project_cleanup_audit.json`

예상 절감 용량:

- Archive candidates: `191.4 MB`
- Delete candidates: `62.7 MB`
- Total if archived externally and delete candidates removed: `254.0 MB`

## 5. 반드시 유지해야 할 정책

- 사용자 명시 지시 없이 실제 삭제/이동 금지.
- `.secrets`는 보안상 유지.
- 운영 핵심 파일과 current daily_news 산출물은 KEEP.
- 정리 실행 전 archive 구조와 삭제 후보를 재확인해야 한다.

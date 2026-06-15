# checkpoint_22

## 1. 현재 완료 상태

- 2026-06-03 일일 뉴스 산출물 `01_news_pool.md`, `02_fact_check.md`, `03_card_brief.md` 생성 완료.
- `pipeline_v3.py` 실행 완료.
- `news_dataset.json` 생성 완료.
- `publish_status=draft` 유지.
- Telegram 승인 게이트 초기화 완료.
- Telegram 승인 요청 실제 전송 완료.
- Telegram Message ID: 220.
- Instagram 게시, Threads 게시, Google Drive 업로드는 실행하지 않음.

## 2. 결정된 규칙

- 승인 전 단계에서는 게시 API를 호출하지 않는다.
- Telegram 승인 요청은 실제 전송하되, Instagram/Threads/Drive는 `APPROVE` 이후에만 실행한다.
- `publish_ledger.json`은 게시 성공 시점에만 업데이트한다.
- 토큰 원문은 보고서와 콘솔 출력에 남기지 않는다.

## 3. 폐기된 선택지

- 승인 없이 바로 Instagram/Threads 게시: 폐기.
- Google Drive 선업로드: 폐기.
- 분야별 분리 제작: 폐기.
- 종합 Threads 1개 게시: 폐기.

## 4. 다음 단계 입력값

- Telegram 응답: `APPROVE` 또는 `REJECT`
- 승인 상태 파일: `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-03/approval_gate/approval_state.json`
- 데이터셋: `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-03/pipeline_v3/news_dataset.json`

## 5. 반드시 유지해야 할 정책

- NEWS_SELECTION_POLICY_V1
- OFFICIAL_IMAGE_POLICY_V1
- EVIDENCE_POLICY_V1
- THREADS_POLICY_V2
- TELEGRAM_APPROVAL_GATE_V1
- 승인 전 Instagram 게시 금지
- 승인 전 Threads 게시 금지
- 승인 전 Google Drive 업로드 금지
- raw token 출력 금지


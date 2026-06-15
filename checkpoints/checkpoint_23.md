# checkpoint_23

## 1. 현재 완료 상태

- 기존 `exported_png/` 산출물을 보류 처리했다.
- 새 카드뉴스 v2를 `exported_png_v2/`에 생성한 뒤, 이미지 품질 한계를 확인하고 v3를 `exported_png_v3/`에 추가 생성했다.
- 카드별 단일 장면 이미지를 `assets_v2/`에 생성했다.
- 뉴스 카드 본문을 육하원칙 구조로 재작성했다.
- contact sheet v2와 contact sheet v3를 생성했다.
- 반복 실수 방지 매뉴얼을 `constitution/daily_card_news_production_manual.md`에 작성했다.
- Instagram 재시도 자동화는 이미 `PAUSED` 상태로 전환했다.

## 2. 결정된 규칙

- 최종 Instagram 카드뉴스는 이미지 없는 임시 렌더링을 사용할 수 없다.
- 뉴스 카드에는 육하원칙이 들어가야 한다.
- 카드별 이미지는 1장만 사용한다.
- 기존본 수정이 아니라 새 버전 폴더를 만들어 교체한다.
- 게시 전 `daily_card_news_production_manual.md` 체크리스트를 따른다.

## 3. 폐기된 선택지

- `exported_png/` 기존 카드뉴스 직접 사용
- 추상 도형 배경 중심 디자인
- 짧은 본문만 있는 초압축 카드
- 이미지 정책 없이 빠른 Instagram 재시도

## 4. 다음 단계 입력값

- 최종 후보 PNG: `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-03/output/exported_png_v3/`
- 미리보기: `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/daily_news/2026-06-03/output/contact_sheet_v3.png`
- 제작 매뉴얼: `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/constitution/daily_card_news_production_manual.md`

## 5. 반드시 유지해야 할 정책

- 이미지 1장 원칙
- 공식 이미지 우선
- 공식 이미지 없을 때만 문맥 기반 생성 이미지
- 육하원칙 본문
- Telegram 승인 후 게시
- Instagram 재시도 전 최신 PNG 폴더 확인
- raw token 출력 금지

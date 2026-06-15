# checkpoint_01

작성일: 2026-06-02

## 1. 현재 완료 상태

- `CONTEXT_COMPACTION_POLICY_V1`을 운영 정책으로 채택했다.
- 앞으로 주요 단계 종료 시 `checkpoint_xx.md`를 생성한다.
- 이후 작업에서는 과거 전체 문서를 다시 읽지 않고, 가장 최신 checkpoint와 현재 작업 파일만 읽는다.
- 경제 뉴스 테스트 카드뉴스 이미지 재교체 작업이 완료됐다.
- 대상 위치: `daily_news_test/economy/2026-06-02/output/`
- 수정 대상 카드: `card_04`, `card_05`, `card_06`, `card_07`, `card_08`
- 수정 파일:
  - `style.css`
  - `assets/image_credits.md`
  - `image_replacement_check.md`
- 샘플 PNG 생성 위치:
  - `image_replacement_sample_png/`
- 샘플 PNG:
  - `card_04_revised.png`
  - `card_05_revised.png`
  - `card_06_revised.png`
  - `card_07_revised.png`
  - `card_08_revised.png`
- 샘플 PNG 해상도는 모두 `1080x1350`으로 확인됐다.
- 전체 PNG export는 아직 진행하지 않았다.

## 2. 결정된 규칙

- 카드뉴스 작업은 최신 checkpoint와 현재 작업 파일만 우선 확인한다.
- 이전 전체 문서 재독해는 금지한다.
- 필요한 경우에만 관련 현재 작업 파일을 직접 확인한다.
- 주요 단계 종료 시 다음 checkpoint를 생성한다.
- checkpoint 파일명은 순차적으로 `checkpoint_02.md`, `checkpoint_03.md`처럼 증가시킨다.
- 경제 뉴스 카드뉴스는 `daily_briefing_light_magazine_v1` 디자인 구조를 유지한다.
- 이미지 교체 시 한 카드에는 이미지 한 장만 사용한다.
- 공식 이미지가 명확하면 공식 이미지 1장을 사용한다.
- 공식 이미지가 없거나 사용 조건이 불명확하면 문맥 기반 AI 생성 이미지 1장을 사용한다.
- 이미지 안에는 텍스트, 가짜 수치, 로고, 실제 인물 얼굴, 실제 기관 발표처럼 보이는 장면을 넣지 않는다.
- 단, 공식 보도자료/공식 인포그래픽 자체에 포함된 텍스트와 수치는 출처 명시 조건으로 허용한다.

## 3. 폐기된 선택지

- card_04, card_06, card_07의 단순 SVG/도형형 이미지는 보류했다.
- card_05의 공식 PDF 표지 이미지는 상단 영역이 비어 보여 최종 적용하지 않았다.
- card_05는 국가데이터처 공식 보도자료 PDF의 요약 인포그래픽 페이지로 교체했다.
- card_08의 기존 단순 수출 SVG 이미지는 보류했다.
- 출처 불명 이미지, 뉴스 기사 이미지, 비공식 재가공 이미지는 사용하지 않았다.
- 전체 11장 PNG export는 아직 진행하지 않았다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_01.md`
- `daily_news_test/economy/2026-06-02/output/image_replacement_check.md`
- 필요 시 현재 작업 파일:
  - `daily_news_test/economy/2026-06-02/output/index.html`
  - `daily_news_test/economy/2026-06-02/output/style.css`
  - `daily_news_test/economy/2026-06-02/output/assets/image_credits.md`

다음 가능한 작업:

- 편집장 샘플 승인 여부 확인
- 승인 시 전체 최종 PNG export
- 저장 위치는 승인 후 새 버전 폴더로 지정
- 예: `daily_news_test/economy/2026-06-02/output/exported_png_final_v2/`

## 5. 반드시 유지해야 할 정책

- `index.html` 텍스트는 승인 없이 수정하지 않는다.
- 디자인 구조, 폰트, 여백, 카드 구조는 승인 없이 수정하지 않는다.
- `card_01~card_03`, `card_09~card_11` 이미지는 별도 지시 없이는 수정하지 않는다.
- 전체 PNG export는 사용자가 승인하거나 명시적으로 지시하기 전까지 금지한다.
- 공식 이미지 사용 시 출처 URL, 이미지 URL, 사용 조건, 접근 날짜를 `assets/image_credits.md`에 기록한다.
- AI 생성 이미지 사용 시 실제 사건 사진처럼 보이게 만들지 않는다.
- 투자 조언성 표현, 시장 예측 단정 표현은 경제 뉴스 카드뉴스에서 금지한다.
- 작업 종료 시 세션 결과, 다음 세션 요약, 다음 작업 지시를 남긴다.

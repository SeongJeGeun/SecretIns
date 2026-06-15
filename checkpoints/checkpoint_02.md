# checkpoint_02

작성일: 2026-06-02

## 1. 현재 완료 상태

- `NO APPROVAL MODE`에 따라 중간 승인 없이 오늘의 뉴스 카드뉴스 제작을 완료했다.
- 작업 위치: `daily_news/2026-06-02/`
- 최근 24시간 공식 발표 중심으로 뉴스 8개를 선별했다.
- `NEWS_SELECTION_POLICY_V1`에 따라 분야별 분리 없이 통합 브리핑으로 제작했다.
- 구조는 `1 + N + 1`이며, N=8로 총 10장이다.
- HTML, CSS, 이미지 자산, PNG export, contact sheet, export report를 생성했다.
- 모든 PNG 해상도는 `1080x1350`이다.
- 제작 중 폐기된 미사용 이미지 2개는 `archive/experiments/daily_news/2026-06-02/unused_assets/`로 이동했다.

## 2. 결정된 규칙

- 통합 일일 뉴스는 `daily_news/YYYY-MM-DD/` 경로를 사용한다.
- 카드뉴스 구조는 커버 1장 + 뉴스 N장 + CTA 1장이다.
- 핵심 원고 근거는 Class A 공식 자료만 사용한다.
- 공식 이미지가 명확하지 않은 카드는 단일 실사풍 AI 생성 이미지를 사용한다.
- 공식 인포그래픽은 이미지 내부 텍스트와 수치를 허용하되 출처를 기록한다.
- PNG export는 `.card` section 자동 감지 방식으로 수행한다.

## 3. 폐기된 선택지

- 공식 근거 URL이 확인되지 않은 한-캐나다 첨단산업 협력 카드는 제외했다.
- K-콘텐츠 성과 카드는 공식 근거 확인 범위가 약해 DMZ 평화의 길 행사로 교체했다.
- 폐기된 이미지 자산 `card_02_kcontent_unused.png`, `card_07_canada_industry_unused.png`는 archive 실험본으로 분류했다.
- 여러 장 이미지 합성, 아이콘, 단순 도형, 뉴스 기사 이미지 무단 사용은 폐기했다.

## 4. 다음 단계 입력값

다음 작업에서 먼저 읽을 파일:

- `checkpoints/checkpoint_02.md`
- `daily_news/2026-06-02/output/export_report.md`
- `daily_news/2026-06-02/output/contact_sheet.png`

현재 작업 파일:

- `daily_news/2026-06-02/03_card_brief.md`
- `daily_news/2026-06-02/output/index.html`
- `daily_news/2026-06-02/output/style.css`
- `daily_news/2026-06-02/output/assets/image_credits.md`

## 5. 반드시 유지해야 할 정책

- 최종 산출물은 `PROJECT_ROOT` 내부에만 생성한다.
- 전체 과거 문서 재독해를 하지 않는다.
- 최신 checkpoint와 현재 작업 파일만 우선 확인한다.
- 다음 주요 단계 종료 시 `checkpoint_03.md`를 생성한다.
- 카드뉴스 이미지는 `1카드 = 1이미지 = 1장면`을 유지한다.
- 공식 근거 없는 새 사실을 추가하지 않는다.
- 민감 주제는 선정적 표현과 개인 사례 연출을 피한다.

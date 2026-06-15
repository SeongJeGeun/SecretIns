# AI Media OS

Obsidian Vault를 공용 두뇌로 사용하는 AI 미디어 운영 시스템이다. Antigravity와 Codex는 직접 대화하지 않고, 같은 Markdown 파일 구조를 읽고 쓰면서 간접 협업한다.

## 1. 시스템 목적

이 시스템은 뉴스를 단순 요약하지 않는다. 사건 단위로 공식 자료, 기사, 전문가 의견, 대중 반응을 모으고, 육하원칙과 본질 후보를 정리한 뒤, 유튜브 롱폼/쇼츠/카드뉴스/블로그/스레드 콘텐츠 패키지로 변환할 수 있는 운영 뼈대를 제공한다.

핵심 철학은 다음과 같다.

- 어려운 세상의 뉴스와 소식을 가장 쉽게 팩트 기반으로 전달한다.
- 헤드라인만 읽고 판단하는 사람이 짧은 시간 안에 사건의 본질을 이해하도록 돕는다.
- 확인되지 않은 정보, 과장, 소설, 역사 왜곡, 투자 추천, 정치 선동을 하지 않는다.
- 공식 자료를 최우선으로 보고 언론 기사는 교차 검증 자료로 사용한다.
- 속보보다 정확성을 우선한다.
- 조회수보다 체류시간, 시청 지속시간, 저장수, 댓글 품질, 재방문율을 더 중요하게 본다.

## 2. Antigravity의 역할

Antigravity는 리서치와 편집 기획을 담당한다.

- 공식 자료, 주요 기사, 전문가 의견, SNS/트렌드 반응 수집
- 확인된 사실과 미확인 정보 분리
- 육하원칙 정리
- 사람들이 궁금해할 질문 도출
- 본질 후보 A/B/C 생성과 위험 요소 분석
- `05_planning_report.md` 작성
- 콘텐츠 제작 전 `06_content_brief.md`의 핵심 판단 채우기

Antigravity는 자료와 판단을 Markdown에 남긴다. Codex에게 직접 지시하지 않고, 다음 작업 지시를 각 파일의 세션 종료 기록에 남긴다.

## 3. Codex의 역할

Codex는 운영 체계와 자동화를 담당한다.

- Vault 폴더 구조 유지
- Markdown 템플릿 관리
- 사건 폴더 자동 생성
- 상태 CSV 업데이트
- 품질 검수 체크리스트 유지
- 사건별 요약 초안 생성
- 저장 규칙과 협업 규칙 정비

Codex는 특정 뉴스 콘텐츠를 임의로 작성하지 않는다. 콘텐츠 본문 작성이 필요할 경우에도 먼저 `01_sources.md`부터 `06_content_brief.md`까지의 근거가 충분한지 확인한다.

## 4. Obsidian Vault 사용 규칙 및 경로 정책

- **모든 최종 산출물은 반드시 PROJECT_ROOT(`media-os/`) 내부에만 저장한다.** 외부 경로(예: `daily_news_test/`, `daily_ai_news/` 등)에 저장하는 것을 엄격히 금지하며, 자세한 가이드라인은 [constitution/path_policy.md](file:///Users/seongjegeun/Documents/SNS_CAN_DO/media-os/constitution/path_policy.md)에 의거한다.
- 모든 산출물은 Markdown 또는 CSV로 저장한다.
- 사건 하나는 `events/{event_id}/` 폴더 하나로 관리한다.
- `_template` 폴더는 원본 템플릿이므로 실제 사건 내용을 직접 적지 않는다.
- 원자료는 `inbox/raw_news/`, 트렌드 자료는 `inbox/trend_data/`에 보관한다.
- 최종 배포용 산출물은 포맷별로 `outputs/` 아래에 저장한다.
- 각 세션 종료 시 반드시 다음 3가지를 남긴다.
  - 이번 세션 결과
  - 다음 세션 요약
  - 다음 작업 지시
- 긴 작업은 한 번에 처리하지 않고 1시간 이내 작업 단위로 나눈다.

## 5. 사건 하나를 처리하는 전체 흐름

1. `scripts/create_event.py`로 새 사건 폴더를 만든다.
2. Antigravity가 `01_sources.md`에 공식 자료와 주요 기사 후보를 정리한다.
3. Antigravity가 `02_six_w.md`에 육하원칙과 불확실한 항목을 정리한다.
4. Antigravity가 `03_questions.md`에 사람들이 궁금해할 질문 5개를 정리한다.
5. Antigravity가 `04_essence_candidates.md`에 본질 후보 A/B/C와 위험 요소를 정리한다.
6. Antigravity가 `05_planning_report.md`에 편집장 보고서를 작성한다.
7. 콘텐츠 제작 전 `06_content_brief.md`에서 대표 본질, 금지 표현, 포함/제외 정보를 고정한다.
8. 포맷별 설계는 `07_youtube_longform.md`부터 `11_threads.md`까지 작성한다.
9. 발행 전 `12_review_notes.md`와 `constitution/quality_checklist.md`로 검수한다.
10. 발행 후 `performance/metrics.csv`와 `performance/comments.md`에 성과와 반응을 기록한다.
11. `13_lessons.md`를 작성하고 핵심만 `memory/` 문서에 압축 반영한다.

## 5-1. 일일 AI 뉴스 브리핑 흐름

`daily_ai_news/`는 `events/`를 대체하지 않는다. `events/`는 사건의 본질을 깊게 해설하는 구조이고, `daily_ai_news/`는 그날 확인된 AI 뉴스를 초압축으로 전달하는 일일 브리핑 구조다.

일일 브리핑 위치:

```text
daily_ai_news/YYYY-MM-DD/
```

기본 파일:

- `01_news_pool.md`: Antigravity가 오늘 AI 뉴스 전부를 수집하고 중복을 병합한다.
- `02_fact_check.md`: 공식 자료, 보조 자료, 불확실한 내용을 분리한다.
- `03_card_brief.md`: 카드뉴스용 초압축 원고와 이미지 슬롯을 정리한다.
- `04_threads.md`: 스레드형 게시글 후보를 정리한다.
- `05_shorts_candidates.md`: 쇼츠 후보를 정리한다.
- `06_longform_candidates.md`: 깊은 해설용 `events/` 승격 후보를 정리한다.
- `07_blog_candidates.md`: 블로그 또는 주간 묶음 후보를 정리한다.
- `assets/`: 공식 이미지, 허용된 AI 생성 이미지, 예외적 스톡 이미지와 출처 기록을 보관한다.
- `output/`: HTML/CSS 렌더링 결과와 PNG export 결과를 보관한다.

뉴스 수 규칙:

| 확인된 뉴스 수 | 카드뉴스 세트 |
|---:|---:|
| 1~7개 | 1세트 |
| 8~14개 | 2세트 |
| 15~20개 | 3세트 |
| 20개 초과 | 중요도 기준 당일 3세트까지 제작, 나머지는 다음 브리핑 후보로 이월 |

카드뉴스 톤:

- 뉴스앵커처럼 차분하고 정확하게 쓴다.
- 문장은 초압축으로 쓴다.
- 스토리텔링과 깊은 해설을 하지 않는다.
- 한 뉴스는 1카드 또는 1섹션으로 처리한다.
- `왜?`를 길게 설명하지 않는다.
- 무슨 일이 있었는지, 핵심 변화, 확인할 점만 남긴다.

이미지 정책:

- 1순위: 기업/기관 공식 뉴스룸, 공식 키노트, 공식 제품, 공식 행사, 공식 보도자료 이미지
- 2순위: 공식 이미지가 없을 경우, 공식 맥락을 분석한 AI 생성 이미지
- 3순위: 스톡 이미지는 원칙적으로 쓰지 않으며, 일반 개념 설명용 배경에만 예외적으로 허용
- 금지: 비공식 재가공 이미지, 뉴스 기사 이미지 무단 사용, 실제 발표처럼 보이는 가짜 AI 이미지, 기업 로고/제품 허위 합성 이미지

## 5-2. 일일 경제 뉴스 테스트 흐름

`daily_news_test/`는 AI 뉴스 외 주제에도 일일 브리핑 구조를 적용할 수 있는지 검증하는 테스트 영역이다. 운영 표준으로 확정된 구조가 아니라, 주제별 위험 요소와 템플릿 재사용 가능성을 먼저 확인하는 실험 구조로 관리한다.

경제 뉴스 테스트 위치:

```text
daily_news_test/economy/YYYY-MM-DD/
```

기본 파일:

- `01_news_pool.md`: 당일 경제 뉴스 후보, 분류, 요약, 콘텐츠 후보 구분을 정리한다.
- `02_fact_check.md`: 공식 출처, 신뢰도 등급, 단정 금지 표현, 투자 조언 위험을 검수한다.
- `03_card_brief.md`: 카드뉴스용 초압축 원고를 정리한다.
- `economy_test_validation.md`: Codex가 HTML/CSS 제작 전 제작 가능 여부와 수정 필요 사항을 평가한다.

경제 뉴스 추가 검수 기준:

- 투자 추천, 매수/매도 유도, 특정 종목 수익 기대 표현을 금지한다.
- 환율, 금리, 주가, 부동산, 원자재 가격의 향후 방향을 단정하지 않는다.
- 수치가 비정상적으로 크거나 현실성과 맞지 않으면 공식 출처 재확인을 요구한다.
- `보도 기준`, `공식 확인 전`, `검토 중` 상태는 카드에 명확히 표시한다.
- 카드뉴스 제작 전 `economy_test_validation.md`에서 제작 가능 판정을 받아야 한다.

템플릿 적용 원칙:

- 현재 확정된 일일 브리핑 카드뉴스 표준은 `daily_ai_news/_template/card_news_html/`의 `daily_briefing_light_magazine_v1`이다.
- 경제 뉴스에도 1장 썸네일, 2~N장 뉴스 브리핑, 마지막 CTA 구조는 재사용 가능하다.
- 단, 경제 뉴스는 투자 조언성 표현과 시장 예측 단정 위험이 높으므로 카드별 본문은 더 짧고 중립적으로 조정해야 한다.

## 6. 상태값 설명

| status | 의미 | 주 담당 |
|---|---|---|
| candidate | 사건 후보로 등록됨 | Antigravity |
| sources_done | 출처 정리 완료 | Antigravity |
| six_w_done | 육하원칙 정리 완료 | Antigravity |
| questions_done | 질문 후보 정리 완료 | Antigravity |
| essence_done | 본질 후보 정리 완료 | Antigravity |
| planning_done | 편집장 보고서 완료 | Antigravity |
| content_brief_done | 콘텐츠 브리프 완료 | Antigravity |
| content_done | 포맷별 콘텐츠 설계 완료 | 담당자 |
| review_done | 발행 전 검수 완료 | Codex/편집장 |
| published | 발행 완료 | 편집장 |
| metrics_done | 성과 지표 기록 완료 | 담당자 |
| lesson_done | 교훈과 메모리 반영 완료 | 담당자 |

상태표 위치: `status/event_status.csv`

필드:

```csv
event_id,event_name,created_at,status,current_step,next_task,owner,priority,last_updated
```

## 7. 새 사건 생성 방법

Vault 루트인 `media-os/` 기준으로 실행한다.

```bash
python3 scripts/create_event.py "사건명"
```

직접 ID를 지정하려면 다음처럼 실행한다.

```bash
python3 scripts/create_event.py "사건명" --event-id 20260602-example-event
```

생성 결과:

- `events/{event_id}/` 아래에 `01_sources.md`부터 `13_lessons.md`까지 복사된다.
- 각 파일 상단에 사건 메타데이터가 붙는다.
- `status/event_status.csv`에 새 행이 추가된다.

상태 업데이트:

```bash
python3 scripts/update_status.py 20260602-example-event sources_done --current-step 02_six_w --next-task "육하원칙을 정리한다." --owner Antigravity
```

사건 요약 생성:

```bash
python3 scripts/summarize_event.py 20260602-example-event
```

## 8. 콘텐츠 생성 전 반드시 확인할 파일

콘텐츠 설계 또는 본문 작성 전 다음 파일을 확인한다.

- `constitution/channel_constitution.md`
- `constitution/editorial_rules.md`
- `constitution/quality_checklist.md`
- `events/{event_id}/01_sources.md`
- `events/{event_id}/02_six_w.md`
- `events/{event_id}/03_questions.md`
- `events/{event_id}/04_essence_candidates.md`
- `events/{event_id}/05_planning_report.md`
- `events/{event_id}/06_content_brief.md`

공식 자료, 불확실 정보, 금지 표현, 대표 본질이 비어 있으면 콘텐츠 제작 단계로 넘기지 않는다.

## 9. 발행 후 metrics.csv에 기록할 지표

성과 기록 위치: `performance/metrics.csv`

필드:

```csv
date,platform,event_id,content_type,title,views,watch_time,retention_rate,saves,shares,comments,followers_gained,return_visits,notes
```

기록 원칙:

- `views`보다 `watch_time`, `retention_rate`, `saves`, `comments`, `return_visits`를 더 중요하게 본다.
- 댓글 수만 보지 말고 댓글의 질문 품질을 `performance/comments.md`에 따로 기록한다.
- 같은 사건의 여러 포맷은 같은 `event_id`로 묶는다.
- 성과가 낮은 콘텐츠도 반드시 기록한다.

## 10. lessons.md를 decision_memory.md에 압축 반영하는 방식

1. 사건 폴더의 `13_lessons.md`에서 실제로 강했던 본질 후보와 질문을 확인한다.
2. 사건명, 날짜, 일회성 수치를 제거하고 반복 가능한 운영 원칙만 남긴다.
3. `memory/decision_memory.md`에는 의사결정 규칙을 3~5줄로 압축한다.
4. 성과가 좋았던 구성은 `memory/successful_patterns.md`에 저장한다.
5. 오해, 과장, 낮은 체류시간을 만든 구성은 `memory/failed_patterns.md`에 저장한다.
6. 반복 댓글과 질문은 `memory/audience_questions.md`에 저장한다.

## 체크포인트 원칙

각 세션은 끝날 때 다음 형식을 남긴다.

```markdown
## 세션 종료 기록

### 이번 세션 결과
- 

### 다음 세션 요약
- 

### 다음 작업 지시
- 
```

다음 작업 지시는 1시간 이내에 끝낼 수 있을 만큼 작게 쓴다.

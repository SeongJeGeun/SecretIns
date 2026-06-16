# AI Media OS (Antigravity 2.0 단독 운영 시스템)

Obsidian Vault나 외부 백그라운드 엔진(Codex)과의 복잡한 연동 없이, **안티그래비티 2.0 단독으로 IT/AI 뉴스를 분석, 카드뉴스 이미지 생성, SNS 자동 업로드 및 청소까지 수행하는 일체형 1인 미디어 자동 운영 시스템**입니다.

---

## 1. 시스템 목적

- 어려운 글로벌 IT/AI 뉴스를 초압축 팩트 기반의 카드뉴스와 Threads 단일 포스트 글로 가공합니다.
- Instagram, Threads, Telegram 채널에 원클릭으로 동시 발행합니다.
- **보안 최우선**: 개인 정보 및 API 토큰이 담긴 `.env` 파일은 절대 외부(GitHub 등)에 유출되지 않도록 철저히 차단합니다.
- **초경량 로컬 유지**: 콘텐츠 업로드 및 텔레그램 보고가 성공적으로 종료되면, 로컬에 남겨진 임시 이미지와 찌꺼기 폴더를 즉시 영구 삭제하여 하드디스크 용량을 확보합니다.

---

## 2. 핵심 실행 구조

안티그래비티 2.0 단독 운영은 다음과 같은 3단계 파이썬 파이프라인으로 작동합니다.

### Step 1. 뉴스 수집 및 다차원 융합 분석 (collect_news.py & AI)
- 최근 24시간 동안 수집된 글로벌 IT/AI 기사에서 **숏폼 관련 트렌드를 배제**하고, 팩트 교차가 가능한 핵심 주제 **최소 6개에서 최대 10개**를 동적으로 선정합니다. (6개 고정 금지)
- 각 주제당 최소 2개 이상의 교차 기사 URL(`related_urls`)을 확보하여 `news_data.json`을 자동 생성합니다.

### Step 2. 미디어 융합 및 이미지 보완 (fuse_news.py & AI)
- `fuse_news.py`를 실행하여 교차 기사들로부터 500px 이상의 유효한 실사 이미지를 수집하고 카드 규격(1080x702)으로 크롭/리사이즈합니다.
- 이미지가 누락되어 `[MISSING_IMAGE_TRIGGER]`가 뜬 카드는 안티그래비티 내장 이미지 생성기(`generate_image`)로 실사풍 이미지를 생성해 완벽히 보완합니다.

### Step 3. 카드뉴스 빌드 및 배포 (build.py & publish.py)
- `build.py`를 통해 가변 카드뉴스 웹 템플릿(1080x1350)과 콘택트 시트를 PNG로 빌드합니다.
- `publish.py`를 실행해 Instagram 캐러셀 피드 및 Threads 단일 포스트(투표 위젯 포함)에 배포합니다.
- **사후 검증 및 청소**: 배포 후 동적 대기(장당 15초)를 거쳐 실제 피드 노출 여부를 API 조회로 사후 검증하고 텔레그램 보고 완료 후 로컬 빌드 파일들을 청소합니다.

---

## 3. 실행 방법 (Usage)

### 3-1. 수동 실행 순서
오늘 자 뉴스를 지금 즉시 수동으로 발행하고 싶을 때 사용하는 흐름입니다.

1. **원고 데이터(`news_data.json`) 생성**
   - AI에게 주제 선정 및 원고 작성을 지시하여 `news_data.json`을 작성합니다.

2. **1차 렌더링 및 이미지 보완**
   ```bash
   python3 daily_news/build.py --data daily_news/news_data.json
   ```
   - 이미지가 빠진 카드가 있다면 AI에게 내장 이미지 생성기로 보충하도록 지시합니다.

3. **최종 배포 및 로컬 청소**
   ```bash
   python3 daily_news/build.py --data daily_news/news_data.json --publish
   ```
   - 인스타그램, 쓰레드 자동 배포 ➔ 텔레그램 보고 ➔ 로컬 찌꺼기 파일 자동 삭제가 한 번에 이루어집니다.

### 3-2. 매일 Scheduled Tasks 자동화 스케줄
본 시스템은 다음과 같이 5단계 크론 스케줄로 구성되어 동작합니다.

#### 1. Step 1: 매일 오전 10:00 (뉴스 수집 및 1차 원고 기획)
- **명령 지시문**:
```text
1. 최근 24시간 글로벌 IT/AI 뉴스를 조사하되 숏폼 관련 토픽은 제외해. 
2. daily_news/topic_weights.json 파일의 키워드 가중치를 읽고, 수집된 기사 중 높은 가중치 키워드를 담은 뉴스가 있다면 이를 최우선(1순위)으로 반영해 최소 6개에서 최대 10개의 핵심 주제를 선정하고(6개 고정 금지), 각 주제별로 2개 이상의 교차 기사를 검색해 related_urls에 담아 news_data.json을 작성해.
3. 글로벌 도달률을 높이기 위해 news_data.json 내의 모든 텍스트(제목, 본문, threads 객체 내의 hook/detail/context/question, 그리고 poll_options 등)는 100% 영문(English)으로만 신규 작성해야 해. 이때 스레드 독자 참여 유도를 위한 2~4개의 투표 선택지(각 25자 이내)도 threads.poll_options 리스트에 반드시 영문으로 작성해줘.
4. python3 daily_news/fuse_news.py 를 실행하여 교차 기사들로부터 고화질(500px 이상) 실제 실사 이미지를 자동으로 융합 및 매칭해.
5. python3 daily_news/build.py --data daily_news/news_data.json 을 1차로 실행해.
6. 만약 이미지를 찾지 못해 터미널에 [MISSING_IMAGE_TRIGGER] 로그가 발생하면, 너의 내장된 이미지 생성 기능(generate_image)을 사용해 기사 맥락에 딱 맞는 실사풍 이미지를 직접 생성해서 보완해.
```

#### 2. Step 2: 매일 오후 12:00 (성과 분석 및 피드백 생성)
- **명령 지시문**:
```text
1. python3 daily_news/analytics.py 를 실행하여 최근 발행된 게시물들의 실시간 도달률, 저장수, 좋아요, 답글 수 통계를 API로 역추적하고, 자가치유를 위한 topic_weights.json 가중치를 갱신해.
2. 텔레그램으로 성과 보고서가 전송되었는지 확인하고, 생성된 daily_news/analytics_report.json이 다음 날 배포 시 정상 참조되도록 유지해.
```

#### 3. Step 3: 매일 오후 14:00 (성과 피드백 반영 및 최종 배포)
- **명령 지시문**:
```text
1. daily_news/analytics_report.json을 직접 읽고 분석해. 너의 내장된 LLM 추론 능력을 사용해, 피드백에 맞춰 당일 10:00에 생성했던 daily_news/news_data.json 원고의 영어 제목과 스레드 훅(hook)을 더 흡입력 있고 도달율이 극대화되도록 직접 리라이팅(Rewriting)하여 갱신해.
2. python3 daily_news/feedback_engine.py 를 실행하여 리라이팅된 news_data.json의 해시태그 최적화 및 JSON 정합성 무결성 검증을 마쳐.
3. 피드백이 반영된 원고를 기반으로 python3 daily_news/build.py --data daily_news/news_data.json 을 다시 실행해 최종 PNG 파일들을 재생성해.
4. 오늘 날짜(KST 기준 YYYY-MM-DD 형식)를 직접 스스로 올바르게 판단한 뒤, python3 daily_news/publish.py --date [오늘날짜] 를 최종 실행하여 인스타그램/스레드 배포를 진행하고, 텔레그램 보고 및 로컬 청소를 완료해.
```

#### 4. Step 4: 매일 오후 16:00 (독자 댓글 분석 및 소통)
- **명령 지시문**:
```text
1. python3 daily_news/comment_manager.py --fetch 를 실행하여 오늘 등록된 미답변 독자 댓글 목록을 수집하고 화면에 출력해.
2. 출력된 미답변 댓글들을 하나씩 분석하여, 독자 댓글이 달린 원본 언어(영어, 한국어 등)를 자동으로 판별해 해당 독자 언어로 동일하게 작성해줘. IT/AI 뉴스 채널의 친절하고 위트 있으며 전문성 있는 어조(해당 언어 기준 100자 내외)로 개별 대댓글 답변 문장을 작성해.
3. 각 댓글마다 python3 daily_news/comment_manager.py --reply --platform [instagram/threads] --id [댓글ID] --message "[답변내용]" 을 실행하여 실시간으로 답글을 실서버에 발행하고 텔레그램 보고가 발송되는지 확인해.
```

#### 5. Step 5: 매일 오후 18:00 (성과 자가치유 및 알고리즘 튜닝)
- **명령 지시문**:
```text
1. 오늘 생성된 daily_news/analytics_report.json 보고서를 자세히 분석해.
2. 너의 내장된 추론 지능으로 독자들이 가장 적극적으로 반응한(Reach, Likes, Saved가 높은) 주제의 영문 회사/테마 명사를 도출해.
3. 도출된 인기 테마는 가중치를 +0.2 상향(최대 2.0)하고, 최근에 노출이 저조했던 기존 테마는 0.9배 감쇠(최소 1.0)하여 daily_news/topic_weights.json의 가중치를 직접 갱신해 저장해. 이 가중치 사전은 다음 날 오전 10:00 기사 수집 및 자동 큐레이션 시에 핵심 뼈대가 되어 알고리즘 노출을 자가치유하게 돼.
```

---

## 5. 다차원 융합 분석 파이프라인 설계도 (FUSION_PIPELINE_V3)

본 시스템은 수집한 기사를 단순 나열하거나 숏폼(릴스 등)으로 배포하지 않으며, 교차 검증 및 미디어 융합 기술을 통해 최고 품질의 IT/AI 카드뉴스를 정제해 내는 독자적인 다차원 융합 분석 파이프라인을 탑재하고 있습니다.

```mermaid
graph TD
    A["1. 수집 & 1차 빌드 (10:00 AM)
    - collect_news.py로 기사 수집
    - AI: topic_weights.json 가중치 반영
    - AI: 6~10개 핵심 뉴스 선정
    - fuse_news.py로 이미지 융합
    - build.py로 1차 HTML/PNG 렌더링"]
    
    B["2. 성과 분석 (12:00 PM)
    - analytics.py 실행
    - 전날 14시 게시물 도달/참여 메트릭 수집
    - 텔레그램 성과 보고 전송
    - analytics_report.json 생성"]
    
    C["3. 피드백 반영 & 배포 (14:00 PM)
    - AI: analytics_report.json 기반 직접 리라이팅
    - feedback_engine.py 실행 (무결성 검증)
    - build.py 재실행 (최종 PNG 재생성)
    - publish.py 실행 (배포 및 로컬 청소)"]
    
    D["4. 독자 대댓글 소통 (16:00 PM)
    - comment_manager.py --fetch로 댓글 수집
    - AI: 독자 언어 감응 개별 대댓글 답변 작성
    - comment_manager.py --reply로 실시간 답글 전송"]

    E["5. 성과 자가치유 (18:00 PM)
    - AI: analytics_report.json 최종 결산분석
    - AI: 잘 터지는 키워드 도출 후 topic_weights.json 갱신
    - 알고리즘 시프트 및 치유 루프 완료"]

    A --> B
    B --> C
    C --> D
    D --> E
    E -.->|"익일 뉴스 수집에 가중치 전달"| A
```

---

## 6. 디렉토리 구조

```text
media-os/
├── .gitignore                   # Git 제외 항목 정의 (.env, node_modules/ 등)
├── README.md                    # 본 시스템 설명서
├── package.json                 # Node.js 패키지 정보 (Playwright 등)
├── memory/
│   └── active_memory.md         # 안티그래비티 행동 규칙 및 카드/스레드 템플릿 정책
└── daily_news/
    ├── .env                     # SNS API 토큰 및 자격 증명 (로컬 전용, 비공개)
    ├── build.py                 # HTML 렌더링 및 PNG 이미지 빌더
    ├── publish.py               # SNS 자동 발행, 텔레그램 보고 및 자동 파일 삭제기
    ├── collect_news.py          # 데일리 AI 뉴스 자동 수집기
    ├── fuse_news.py             # 미디어 융합 및 이미지 매칭 분석기
    ├── news_data.json           # 오늘 자 카드뉴스 및 쓰레드 원고 데이터
    ├── publish_history.json     # 중복 업로드 방지용 기록부
    ├── raw_news_pool.json       # collect_news가 가져온 원시 뉴스 모음
    └── template/                # 카드뉴스 웹 템플릿 리소스 (CSS, BG 이미지 등)
```

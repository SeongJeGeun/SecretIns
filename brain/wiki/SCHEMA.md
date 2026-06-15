# Obsidian Wiki SCHEMA

이 문서는 로컬 AI 오케스트라의 RAG 두뇌(`brain/wiki/`)를 관리하기 위한 에이전트용 스키마 및 가이드라인입니다.

## 1. 폴더 구조

```text
brain/wiki/
├── topics/        # 주요 기술 및 비즈니스 주제 (예: AI_반도체.md, 온디바이스_AI.md)
├── entities/      # 주요 회사 및 핵심 인물 (예: OpenAI.md, Google.md, Sam_Altman.md)
├── trends/        # 월간/분기별 트렌드 추적 노드 (예: 2026-06_AI에이전트.md)
├── performance/   # 성과 패턴 (high_engagement.md, failed_patterns.md)
└── SCHEMA.md      # 본 문서
```

## 2. 노드 명명 규칙

- 파일명은 영문/한글 모두 가능하며, 공백 대신 언더바(`_`)를 사용합니다. (예: `AI_반도체.md`, `Tesla.md`)
- 주제 파일명은 명사형 단어로 통일합니다.

## 3. 링크 작성 규칙 (`[[wikilinks]]`)

- 본문 중 다른 위키 노드를 지칭할 때는 반드시 대괄호 두 개를 감싸서 링크를 형성합니다.
  - 예: `최근 [[Google]]이 발표한 AI 에이전트는 [[AI_반도체]] 시장의 큰 변화를...`
- 존재하지 않는 노드라도 중요 실체(Entity) 또는 주제(Topic)라면 링크를 생성합니다. (Obsidian의 고아 노드로 남아 나중에 채워집니다)

## 4. 콘텐츠 업데이트 규칙 (사서 에이전트 동작)

1. **내용 누적**: 기존 문서를 지우고 새로 쓰지 말고, 최신 팩트를 날짜 기입과 함께 상단 또는 하단에 누적하여 추가합니다.
2. **모순 해결**: 기존 지식과 상충하는 새로운 공식 뉴스가 발표된 경우, 기존 내용을 지우지 않고 "2026-06-09 기준 업데이트: 기존의 ~ 발표는 ~로 대체됨"과 같이 변경 이력을 기록합니다.
3. **태그 달기**: 각 문서의 최상단에 YAML Frontmatter 메타데이터를 추가합니다.
   ```markdown
   ---
   type: topic | entity | trend
   last_updated: YYYY-MM-DD
   tags: [AI, Semiconductor, Google]
   ---
   ```

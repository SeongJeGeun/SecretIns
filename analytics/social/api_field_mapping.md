# Instagram + Threads API Field Mapping

작성일: 2026-06-02

## Instagram

### 게시물 메타데이터

- Endpoint: `GET https://graph.facebook.com/v19.0/{ig_media_id}`
- Fields: `id,caption,media_type,permalink,timestamp,like_count,comments_count`
- 저장 시트: `instagram_posts`

### 게시물 인사이트

- Endpoint: `GET https://graph.facebook.com/v19.0/{ig_media_id}/insights`
- Metrics: `reach,likes,comments,saved,shares`
- 저장 시트: `instagram_posts`

### 계정 스냅샷

- Endpoint: `GET https://graph.facebook.com/v19.0/{ig_user_id}`
- Fields: `id,username,followers_count,media_count`
- 저장 시트: `instagram_posts`, `daily_summary`

### 요청 항목별 처리

| 요청 항목 | 수집 방식 | 저장 필드 | 자동화 가능 여부 | 주의 |
|---|---|---|---|---|
| Reach | media insights | `reach` | 가능 | 계정/콘텐츠 상태에 따라 제한될 수 있음 |
| Likes | media metadata 또는 insights | `likes` | 가능 | `like_count`를 우선 사용 |
| Comments | media metadata 또는 insights | `comments` | 가능 | `comments_count`를 우선 사용 |
| Saves | media insights | `saves` | 가능 | API metric 이름은 `saved` |
| Shares | media insights | `shares` | 가능 | 콘텐츠 유형/권한에 따라 빈 값 가능 |
| Followers Gained | 계정 팔로워 수 전후 차이 | `followers_gained` | 부분 가능 | 게시물 단일 지표가 아니므로 발행 전후 스냅샷 필요 |

## Threads

### 게시물 메타데이터

- Endpoint: `GET https://graph.threads.net/v1.0/{threads_post_id}`
- Fields: `id,permalink,text,timestamp,media_type`
- 저장 시트: `threads_posts`

### 게시물 인사이트

- Endpoint: `GET https://graph.threads.net/v1.0/{threads_post_id}/insights`
- Metrics: `views,likes,replies,reposts,quotes,shares`
- 저장 시트: `threads_posts`

### 요청 항목별 처리

| 요청 항목 | 수집 방식 | 저장 필드 | 자동화 가능 여부 | 주의 |
|---|---|---|---|---|
| Views | post insights | `views` | 가능 | 게시 후 반영 지연 가능 |
| Likes | post insights | `likes` | 가능 | 공개/권한 상태에 따라 제한 가능 |
| Replies | post insights | `replies` | 가능 | 댓글 품질 분석은 별도 수집 필요 |
| Reposts | post insights | `reposts` | 가능 | 공유성 판단 지표 |
| Quotes | post insights | `quotes` | 가능 | 맥락 확산 지표 |
| Shares | post insights | `shares` | 응답 확인 후 가능 | API 버전/계정 상태에 따라 미제공 가능 |

## 계산 지표

- Instagram engagement: `likes + comments + saves + shares`
- Instagram save rate: `saves / reach`
- Instagram share rate: `shares / reach`
- Threads engagement: `likes + replies + reposts + quotes + shares`
- Threads reply rate: `replies / views`
- Threads repost quote rate: `(reposts + quotes) / views`

## 보안

- 토큰은 환경변수에서만 읽는다.
- 보고서에는 토큰 원문을 저장하지 않는다.
- 실패 응답 저장 시 토큰 파라미터는 마스킹한다.

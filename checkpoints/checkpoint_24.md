# checkpoint_24

## 1. 현재 완료 상태

- 인증정보 읽기 경로를 `.secrets/.env.scheduler`로 고정했다.
- Keychain fallback을 제거했다.
- 예전 키 이름 `INSTAGRAM_IG_USER_ID`, `THREADS_USER_ID` 사용을 제거했다.
- 스크립트 문법 검사를 통과했다.
- 자동화는 생성하지 않았다.

## 2. 결정된 규칙

- 게시 자동화와 수동 실행은 사용자가 제공해 저장한 `.env.scheduler` 값만 읽는다.
- 외부 shell 환경변수나 Keychain 값은 신뢰하지 않는다.
- raw token은 출력하지 않는다.
- PRESENT/ABSENT 검증만 허용한다.

## 3. 폐기된 선택지

- 토큰을 매번 사용자에게 다시 요청
- shell 환경변수 우선 사용
- Keychain fallback 사용
- 예전 계정 ID 키 이름 유지

## 4. 다음 단계 입력값

- 비밀값 파일: `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/.secrets/.env.scheduler`
- 공통 로더: `/Users/seongjegeun/Documents/SNS_CAN_DO/media-os/scripts/scheduler_env.py`

## 5. 반드시 유지해야 할 정책

- `.env.scheduler`만 공식 인증정보 소스로 사용
- raw token 출력 금지
- 자동화 생성 금지 지시가 있을 때 자동화 생성 금지
- 게시 전 품질 게이트 유지


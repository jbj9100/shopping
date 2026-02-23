---
trigger: always_on
---

## 0) 기본 답변/작업 방식
- 답변은 한국어로 작성한다.
- 코드 변경 전 항상 아래 3줄 요약을 먼저 작성한다.
  - 변경: ...
  - 이유: ...
  - 영향: ...
- 파일 생성/수정 시: 불필요한 대규모 리팩터링 금지. 요청 범위만 최소 변경한다.
- 터미널 명령은 실행 전에 "무슨 명령 / 왜 필요한지"를 한 줄로 설명한다.
- 불확실하면 추측하지 말고, 확인 방법(명령/체크리스트)을 먼저 제시한다.

## 1) 프로젝트 디렉터리 규칙 (조건부 적용)
- 아래 규칙은 작업 대상 파일 경로에 따라 적용한다.
  - `front/**` 작업이면: Frontend Rules만 + Base Rules 적용
  - `backend/**` 작업이면: Backend Rules만 + Base Rules 적용
  - 그 외 경로면: Base Rules만 적용

---

# Frontend Rules (React) — `front/**` 작업 시에만 적용
- `front/` 디렉터리는 React로 개발한다.
- 프론트 코드는 `front/` 안에만 둔다. (백엔드/DB 코드 섞지 않는다)
- React 컴포넌트/라우팅/상태관리는 프론트에서만 처리하고, 서버 로직(쿼리/세션/SQLAlchemy 등)을 넣지 않는다.
- API 호출은 백엔드 엔드포인트를 기준으로 분리해서 작성한다.
- json을 backend로 넘길때 axios로 만들어야한다.

---

# Backend Rules (FastAPI, Python 3.10.19) — `backend/**` 작업 시에만 적용
## 2) 기술 스택/버전 고정
- `backend/` 디렉터리는 FastAPI로 개발한다.
- Python 버전은 3.10.19 기준으로만 코드를 작성한다.
- Python 3.11+ 전용 기능은 사용하지 않는다.
  - 예: `tomllib`, `typing.Self`, `StrEnum`, `asyncio.TaskGroup` 등

## 3) 백엔드 폴더 구조 (권장 표준)
- 백엔드는 아래 구조를 따른다(새 파일 생성 시 이 구조를 우선한다).
  - `backend/main.py` : FastAPI 앱 엔트리포인트(라우터 include, 미들웨어/핸들러 등록)
  - `backend/routers/*.py` : API 라우터(HTTP 계층)
  - `backend/schemas/*.py` : Pydantic 요청/응답 스키마
  - `backend/services/*_service.py` : 도메인 서비스(비즈니스 로직)
  - `backend/repositories/*_repository.py` : DB 접근(쿼리/CRUD만)
  - `backend/models/*.py` : SQLAlchemy 모델
  - `backend/db/session.py` : 엔진/세션 팩토리/Base
  - `backend/core/*.py` : config/security/logging 등 공통
  - `backend/exceptions/*` : 커스텀 예외 + 핸들러
  - `backend/utils/*` : 유틸

## 4) 레이어 경계(가장 중요)
### 4.1 routers (HTTP 계층)
- routers는 FastAPI를 사용한다. (`APIRouter`, `Depends`, `Request`, `Response`, status code 사용 가능)
- routers의 책임: 입력 검증(schemas) → service 호출 → 응답(schemas) 반환
- 금지:
  - routers에서 DB 쿼리 직접 호출 금지(Repository 직접 호출 금지)
  - routers에서 SQLAlchemy 모델 직접 조작 금지(가능하면 service/repo로 이동)

### 4.2 services (도메인/비즈니스 로직)
- services는 “FastAPI를 몰라도 되게” 작성한다.
- 금지(services에서 사용하지 말 것):
  - `APIRouter`, `Depends`, `Request`, `Response`, `HTTPException` 등 FastAPI 전용 객체/예외
- 허용:
  - repositories 호출
  - 도메인 규칙(검증/상태 전이/권한/중복 체크 등)
  - 필요 시 Pydantic(schemas) 사용은 허용하되, HTTP 개념을 끌고 오지 않는다.
- 예외 처리 원칙:
  - services는 `exceptions/custom_exceptions.py`의 커스텀 예외를 raise 한다.
  - HTTP 상태코드 변환은 handlers에서만 한다.

### 4.3 repositories (DB 접근 전용)
- repositories의 책임: SQLAlchemy Session을 받아 쿼리/CRUD만 수행
- 금지:
  - 비즈니스 규칙(“가입 가능 여부”, “권한 체크”)은 repositories에 넣지 않는다(services로)
  - FastAPI 의존성(Depends/Request 등) 사용 금지

### 4.4 models (DB 모델)
- models는 SQLAlchemy 모델 정의만 포함한다.
- 비즈니스 로직/서비스 로직은 models에 넣지 않는다.

## 5) DB 세션 전달 규칙(표준 플로우)
- DB 세션은 router에서 의존성으로 생성/주입하고(service→repo로 전달) 사용한다.
  - router: `db = Depends(get_db)` 형태
  - service 함수 시그니처에 `db`를 인자로 받고
  - repo 호출 시 `db`를 그대로 넘긴다.
- 세션 생성/엔진 설정은 `backend/db/session.py`에서만 관리한다.

## 6) 답변 시 컨텍스트 확인 규칙
- 백엔드 작업 요청을 받으면, 먼저 “수정 대상 경로(front인지 backend인지)”를 기준으로 규칙을 적용한다.
- Pydantic/FastAPI 버전이 중요해 보이면, 추측하지 말고 버전 확인 방법을 먼저 제시한다.
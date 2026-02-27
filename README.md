# 🛒 Shopping Mall Project

마이크로서비스 기반 쇼핑몰 애플리케이션입니다.  
FastAPI(Backend) + React(Frontend) + Kafka 이벤트 스트리밍 + WebSocket 실시간 통신으로 구성되어 있으며, Kubernetes 환경에서 배포됩니다.

---

## 📐 아키텍처 개요

```
[Frontend (React + Vite)]
        │  REST API / WebSocket
        ▼
[Backend (FastAPI)]  ──(Outbox Event)──▶  [Publisher]
        │                                       │
        │  PostgreSQL                           │  Kafka Topics
        ▼                                       ▼
   [PostgreSQL DB]              ┌──────────────────────────────┐
                                │  consumer-analytics          │
                                │  consumer-stock              │
                                └──────────────────────────────┘
                                              │
                                              ▼
                                    [WebSocket Server]
                                              │
                                              ▼
                                    [Frontend (실시간 Push)]
```

---

## 📁 프로젝트 구조

```
shopping/
├── backend/              # FastAPI 메인 백엔드
├── frontend/             # React + Vite 프론트엔드
├── websocket/            # WebSocket 서버 (실시간 Push)
├── publisher/            # Transactional Outbox Publisher
├── consumer-analytics/   # Kafka Consumer (매출/통계)
├── consumer-stock/       # Kafka Consumer (재고)
├── k6/                   # 부하 테스트 (k6)
├── Images_category/      # 카테고리 이미지 저장소
└── Images_products/      # 상품 이미지 저장소
```

---

## 🔧 서비스별 상세 구조

### 1. `backend/` — FastAPI 메인 백엔드

**기술스택:** Python 3.10 / FastAPI / SQLAlchemy / PostgreSQL / Redis / MinIO / aiokafka

```
backend/
├── main.py                  # FastAPI 앱 엔트리포인트
├── requirements.txt
├── Dockerfile
├── init_data.sql            # 초기 데이터 SQL
├── api/
│   └── shop/
│       └── routers/         # HTTP 라우터
│           ├── login.py     # 로그인 / 회원가입 / 로그아웃 / 마이페이지
│           ├── auth.py      # JWT 토큰 갱신
│           ├── orders.py    # 주문
│           ├── products.py  # 상품
│           ├── category.py  # 카테고리
│           ├── carts.py     # 장바구니
│           ├── images.py    # 이미지 업로드
│           └── admin.py     # 관리자
├── core/
│   ├── auth/                # JWT 인증/인가
│   ├── deps/                # FastAPI 의존성 (get_db 등)
│   ├── lifespan/            # DB/Redis 연결 lifespan
│   └── middlewares/         # 커스텀 미들웨어
├── models/                  # SQLAlchemy 모델
├── schemas/                 # Pydantic 요청/응답 스키마
├── services/                # 비즈니스 로직
├── repositories/            # DB CRUD
├── exceptions/              # 커스텀 예외 + 핸들러
├── constants/               # 상수 정의
├── db/                      # DB 세션/엔진
└── k8s/                     # Kubernetes 매니페스트
    ├── configmap.yaml
    ├── deployment.yaml
    ├── service.yaml
    └── namespace.yaml
```

**주요 API 엔드포인트:**

| 라우터 | 경로 | 설명 |
|--------|------|------|
| login | `/login`, `/signup`, `/logout` | 인증 |
| auth | `/auth/refresh` | JWT 토큰 갱신 |
| products | `/products` | 상품 CRUD |
| category | `/category` | 카테고리 |
| orders | `/orders` | 주문 |
| carts | `/carts` | 장바구니 |
| images | `/images` | MinIO 이미지 업로드 |
| admin | `/admin` | 관리자 대시보드 |

---

### 2. `frontend/` — React + Vite 프론트엔드

**기술스택:** React 18 / Vite 5 / Axios / React Router v6 / Chart.js / Nginx

```
frontend/
├── index.html
├── vite.config.js
├── nginx.conf               # Nginx 설정 (SPA 라우팅)
├── Dockerfile
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css
│   ├── pages/               # 페이지 컴포넌트
│   │   ├── HomePage.jsx          # 메인 (상품 목록 + 실시간 대시보드)
│   │   ├── LoginPage.jsx
│   │   ├── SignupPage.jsx
│   │   ├── ProductDetailPage.jsx
│   │   ├── CartPage.jsx
│   │   ├── OrderPage.jsx
│   │   ├── OrderHistoryPage.jsx
│   │   ├── OrderDetailPage.jsx
│   │   ├── MyPage.jsx
│   │   ├── AdminPage.jsx         # 관리자 페이지
│   │   ├── AdminDashboard.jsx
│   │   ├── DashboardPage.jsx
│   │   └── FlashSaleQueuePage.jsx  # 플래시 세일 대기열
│   ├── components/          # 공통 컴포넌트
│   │   ├── common/          # 버튼, 모달 등
│   │   ├── layout/          # 헤더, 푸터 등
│   │   ├── product/         # 상품 카드, 목록
│   │   ├── stock/           # 재고 표시
│   │   ├── price-alert/     # 가격 알림
│   │   ├── price-drop/      # 가격 인하
│   │   ├── recommendation/  # 추천 상품
│   │   ├── MiniDashboard.jsx
│   │   ├── RealtimeDashboard.jsx
│   │   └── TopProductsTable.jsx
│   ├── services/            # API 호출 모듈 (axios)
│   ├── contexts/            # React Context
│   ├── hooks/               # Custom Hooks
│   ├── store/               # 전역 상태
│   └── styles/              # 공통 스타일
└── k8s/                     # Kubernetes 매니페스트
```

---

### 3. `websocket/` — WebSocket 서버

**기술스택:** Python 3.10 / FastAPI WebSocket / aiokafka

실시간 이벤트(재고 변경, 매출 통계, 플래시 세일 대기열)를 Kafka에서 소비하여 연결된 Frontend 클라이언트에 Push합니다.

```
websocket/
├── main.py               # FastAPI WebSocket 엔드포인트
├── websocket_manager.py  # 채널별 연결 관리
├── kafka_consumer.py     # Kafka 이벤트 소비 → broadcast
├── requirements.txt
├── Dockerfile
└── k8s/
    ├── configmap.yaml
    ├── deployment.yaml
    ├── service.yaml
    └── namespace.yaml
```

**WebSocket 채널:**

| 채널 | 경로 | 설명 |
|------|------|------|
| stock | `/websocket/ws/stock` | 재고 변경 실시간 알림 |
| analytics | `/websocket/ws/analytics` | 매출/통계 실시간 업데이트 |
| flash_queue | `/websocket/ws/flash_queue` | 플래시 세일 대기열 상태 |

---

### 4. `publisher/` — Transactional Outbox Publisher

**기술스택:** Python 3.10 / aiokafka / SQLAlchemy / PostgreSQL

Transactional Outbox 패턴으로 DB의 `outbox` 테이블을 폴링하여 Kafka 토픽으로 이벤트를 발행합니다.

```
publisher/
├── main.py            # OutboxPublisher (poll & publish 루프)
├── db/                # DB 연결 (conn_db.py)
├── models/            # Outbox 모델
├── repositories/      # rep_outbox.py (pending 이벤트 조회)
├── requirements.txt
├── Dockerfile
└── k8s/
    ├── configmap.yaml
    ├── deployment.yaml
    ├── service.yaml
    └── namespace.yaml
```

---

### 5. `consumer-analytics/` — 매출/통계 Consumer

**기술스택:** Python 3.10 / aiokafka / SQLAlchemy / PostgreSQL

Kafka에서 주문 이벤트를 소비하여 매출 통계 DB를 갱신하고 WebSocket 채널로 브로드캐스트합니다.

```
consumer-analytics/
├── main.py        # Kafka Consumer 루프
├── db/            # DB 연결
├── models/        # 통계 모델
├── services/      # 비즈니스 로직
├── requirements.txt
├── Dockerfile
└── k8s/
```

---

### 6. `consumer-stock/` — 재고 Consumer

**기술스택:** Python 3.10 / aiokafka / SQLAlchemy / PostgreSQL

Kafka에서 재고 관련 이벤트를 소비하여 재고 DB를 갱신하고 WebSocket 채널로 브로드캐스트합니다.

```
consumer-stock/
├── main.py        # Kafka Consumer 루프
├── db/            # DB 연결
├── models/        # 재고 모델
├── repositories/  # DB CRUD
├── requirements.txt
├── Dockerfile
└── k8s/
```

---

### 7. `k6/` — 부하 테스트

**기술스택:** k6 / JavaScript

```
k6/
├── shopping.js      # 메인 부하 테스트 시나리오
├── create-users.sh  # 테스트 사용자 생성 스크립트
├── users.csv        # 테스트 사용자 데이터
├── run.sh           # k6 실행 스크립트
└── README.md
```

---

## ☸️ Kubernetes 배포

각 서비스는 독립적인 `k8s/` 디렉터리를 가지며 다음 매니페스트로 구성됩니다:

| 파일 | 설명 |
|------|------|
| `namespace.yaml` | 네임스페이스 정의 |
| `configmap.yaml` | 환경변수 설정 |
| `deployment.yaml` | Pod 배포 설정 |
| `service.yaml` | 서비스 노출 설정 |

---

## 🛠️ 기술 스택 요약

| 영역 | 기술 |
|------|------|
| Frontend | React 18, Vite 5, Axios, Chart.js, React Router v6 |
| Backend | FastAPI, Python 3.10, SQLAlchemy, Pydantic v2 |
| Database | PostgreSQL, Redis |
| 이벤트 스트리밍 | Apache Kafka (aiokafka) |
| 파일 스토리지 | MinIO |
| 실시간 통신 | WebSocket (FastAPI) |
| 컨테이너 | Containerd |
| 오케스트레이션 | Kubernetes |
| 부하 테스트 | k6 |
| 관측성 | OpenTelemetry  |
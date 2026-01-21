# Shopping Load Test (K6)

쇼핑몰 프로젝트의 부하 테스트를 위한 K6 스크립트입니다.

## 📁 파일 구조

```
k6/
├── shopping.js          # 메인 테스트 스크립트
├── users.csv            # 테스트 계정 목록 (100개)
├── create-users.sh      # 계정 생성 스크립트
├── run.text             # 실행 명령어
└── README.md            # 이 파일
```

## 🚀 빠른 시작

### 1. 테스트 계정 생성

먼저 백엔드에 테스트 계정을 생성해야 합니다:

```bash
# Linux/Mac
chmod +x create-users.sh
./create-users.sh

# Windows (Git Bash)
bash create-users.sh
```

**또는 SQL로 직접 생성:**
```sql
-- PostgreSQL에서 실행 (비밀번호 해시는 실제 값으로 교체)
DO $$
BEGIN
  FOR i IN 1..100 LOOP
    INSERT INTO users (email, username, password_hash, role, created_at)
    VALUES (
      'loadtest' || i || '@test.com',
      'LoadTest' || i,
      -- 아래는 'test1234'의 Argon2 해시 (실제 환경에 맞게 변경)
      '$argon2id$v=19$m=65536,t=3,p=4$...',
      'user',
      NOW()
    )
    ON CONFLICT (email) DO NOTHING;
  END LOOP;
END $$;
```

### 2. K6 테스트 실행

```bash
# run.text의 환경변수 설정 후 실행
export K6_PROMETHEUS_RW_SERVER_URL=http://k6-kube-prometheus-stack-prometheus:9090/api/v1/write
export K6_PROMETHEUS_RW_TREND_STATS="p(0.5),p(0.9),p(0.95),p(0.99),min,max,avg,count"
k6 run -o experimental-prometheus-rw --tag testid="run-02" shopping.js
```

## 🛒 테스트 시나리오

### 쇼핑 플로우 (모든 VU)

1. **로그인** (`/api/shop/login/`)
   - CSV에서 계정 정보 로드 (순환)
   - JWT Access Token 획득

2. **상품 선택**
   - 랜덤으로 1~3개 상품 선택

3. **장바구니 추가** (`/api/shop/cart/`)
   - 선택한 상품들을 장바구니에 추가
   - 수량: 1~3개 (랜덤)

4. **장바구니 확인** (`/api/shop/cart/`)
   - GET 요청으로 장바구니 조회

5. **주문하기** (`/api/shop/orders/`)
   - 주문 생성
   - 배송 정보 포함

## 📊 부하 패턴

```
VUs
100 |           ╱‾‾‾‾‾‾‾‾╲
 50 |    ╱‾‾‾‾‾╯          │
 10 |╱‾‾‾╯                │
  0 |════════════════════╲╱
     0  30s  1m   3m   4m  4.5m
```

- **0-30s**: 10명까지 워밍업
- **30s-1m30s**: 50명까지 증가
- **1m30s-3m30s**: 50명 유지
- **3m30s-4m**: 100명으로 스파이크
- **4m-5m**: 100명 유지
- **5m-5m30s**: 0명으로 감소

## 📈 성능 목표 (Thresholds)

- **에러율**: 5% 미만
- **응답 시간 (p95)**: 3초 미만

## 🔧 커스터마이징

### URL 변경
`shopping.js`의 `BASE_URL` 수정:
```javascript
const BASE_URL = 'https://your-domain.com/api/shop';
```

### 부하 패턴 조정
`options.scenarios.shopping_flow.stages` 수정:
```javascript
stages: [
  { duration: '1m', target: 20 },   // 1분 동안 20명까지
  { duration: '3m', target: 20 },   // 3분 동안 20명 유지
  { duration: '30s', target: 0 },   // 30초 동안 종료
],
```

### 테스트 계정 추가
`users.csv`에 행 추가:
```csv
loadtest101@test.com,test1234
loadtest102@test.com,test1234
```

## 📌 주의사항

1. **테스트 계정 필수**: `users.csv`의 계정들이 실제 백엔드에 존재해야 함
2. **비밀번호 동일**: 모든 계정의 비밀번호는 `test1234`
3. **상품 데이터**: 백엔드에 상품 데이터가 있어야 테스트 가능
4. **VU 수 vs 계정 수**: VU가 100개를 초과하면 계정이 순환됨

## 🐛 문제 해결

### 로그인 실패 (401)
```
✗ login OK
```
→ `create-users.sh` 실행 또는 SQL로 계정 생성 확인

### 상품 없음
```
Setup: Loaded 0 products
```
→ 백엔드 상품 데이터 확인: `curl https://shopping.project.com/api/shop/products/`

### HTTPS 인증서 에러
→ `insecureSkipTLSVerify: true` 이미 설정됨 (테스트 환경용)

## 📊 모니터링

Grafana 대시보드:
- URL: http://192.168.80.90:30090 (또는 설정된 Prometheus 주소)
- Test ID로 필터링: `testid="run-02"`

### 주요 메트릭
- `http_req_duration`: 응답 시간
- `http_req_failed`: 에러율
- `http_reqs`: 초당 요청 수
- `vus`: 동시 사용자 수
- 태그별 분류: `login`, `add_to_cart`, `view_cart`, `checkout`

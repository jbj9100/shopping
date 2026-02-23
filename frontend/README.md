# Shopping Front

React + Vite 기반 쇼핑몰 프론트엔드

## 개발 환경 설정

### 1. 의존성 설치
```bash
cd front
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

개발 서버가 `http://localhost:5173`에서 실행됩니다.

### 3. 프로덕션 빌드
```bash
npm run build
```

## 주요 기능

- **실시간 업데이트**: WebSocket을 통한 가격 변동, 재고 알림
- **상품 목록**: 카테고리별, 검색, 필터링
- **장바구니**: 상품 추가, 수량 조절, 삭제
- **반응형 디자인**: 모바일, 태블릿, 데스크탑 대응

## 기술 스택

- React 18
- Vite
- React Router v6
- Axios
- Vanilla CSS

## 백엔드 연동

백엔드 서버가 `http://localhost:8000`에서 실행 중이어야 합니다.
Vite 프록시 설정으로 `/api` 경로가 자동으로 백엔드로 연결됩니다.

## 참고

- WebSocket 연결 실패는 정상입니다 (백엔드가 준비되면 자동 연결됨)
- 백엔드 미연결 시 목업 데이터가 표시됩니다

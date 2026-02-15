# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Package 설치
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# 소스 복사 및 빌드
COPY . .

# Vite를 node로 직접 실행 (Podman 권한 문제 해결)
RUN node node_modules/vite/bin/vite.js build

# Runtime stage
FROM nginx:alpine

# Built 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx.conf는 ConfigMap에서 마운트됨

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

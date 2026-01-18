# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Package 설치
COPY package.json package-lock.json ./
RUN npm ci

# 소스 복사 및 빌드
COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine

# Nginx 설정
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

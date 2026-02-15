FROM 192.168.80.90:5000/python:3.10.19-slim

WORKDIR /app

# 192.168.80.90:5000/python:3.10.19-slim안에서 미리함
# 시스템 패키지 업데이트
# RUN apt-get update && apt-get install -y \
#     gcc \
#     postgresql-client \
#     && rm -rf /var/lib/apt/lists/*

# Requirements 설치
COPY requirements.txt .

ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

# devpi에 캐시하기 위함
RUN pip install --no-cache-dir \
    -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} \
    -r requirements.txt

# 소스 복사
COPY . .

# 환경변수
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

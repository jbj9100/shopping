FROM 192.168.80.90:5000/python:3.10.19-slim2

WORKDIR /app

# 192.168.80.90:5000/python:3.10.19-slim안에서 미리함
# 시스템 패키지 업데이트
# RUN apt-get update && apt-get install -y \
#     curl \
#     gcc \
#     postgresql-client \
#     && rm -rf /var/lib/apt/lists/*
# RUN curl -sSL -o /usr/local/bin/yq \
#     https://github.com/mikefarah/yq/releases/download/${YQ_VER}/yq_linux_amd64 \
#  && chmod +x /usr/local/bin/yq \
#  && yq --version

# pip 잡설/버전체크 줄이기(미세 최적화) + pyc 생성 방지
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1


# Requirements 설치
COPY requirements.txt .

ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

# devpi에 캐시하기 위함
RUN pip install -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} \
    -r requirements.txt

# 소스 복사
COPY . .

# 환경변수
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

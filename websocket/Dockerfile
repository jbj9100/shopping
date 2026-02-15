FROM 192.168.80.90:5000/python:3.10.19-slim

WORKDIR /app

# Requirements 설치
COPY requirements.txt .
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

RUN pip install -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} \
    -r requirements.txt
# 소스 복사
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["python", "main.py"]

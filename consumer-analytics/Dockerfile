FROM 192.168.80.90:5000/python:3.10.19-slim2

WORKDIR /app

# pip 잡설/버전체크 줄이기(미세 최적화) + pyc 생성 방지
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1


COPY requirements.txt .
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

RUN pip install -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} \
    -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "main.py"]

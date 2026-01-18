FROM python:3.10.19-slim

WORKDIR /app

# Requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["python", "main.py"]

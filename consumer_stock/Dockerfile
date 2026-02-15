FROM python:3.10.19-slim

WORKDIR /app

COPY requirements.txt .
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

RUN pip install --no-cache-dir \
    -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} \
    -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]

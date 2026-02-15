FROM 192.168.80.90:5000/python:3.10.19-slim2

WORKDIR /app

COPY requirements.txt .
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

RUN pip install -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST} \
    -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]

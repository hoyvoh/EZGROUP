FROM python:3.12.4-alpine
WORKDIR /api
COPY . .
RUN apk add gcc musl-dev libffi-dev mariadb-dev
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

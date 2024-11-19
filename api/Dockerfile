FROM python:3.12.4-alpine
WORKDIR /api
COPY . /api
RUN pip install -r requirements.txt
COPY .env /api/.env
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

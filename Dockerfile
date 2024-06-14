FROM python:3.10

EXPOSE 8000

WORKDIR /docker-watchmate

COPY . /docker-watchmate

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
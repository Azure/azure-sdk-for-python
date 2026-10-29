FROM mcr.microsoft.com/mirror/docker/library/python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8088

CMD ["python", "main.py"]

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY *.whl .
COPY main.py .
COPY agent.yaml .

RUN pip install -r requirements.txt && \
    pip install --no-cache-dir azure_ai_agentserver_core-1.0.0b7-py3-none-any.whl && \
    pip install --no-cache-dir azure_ai_agentserver_agentframework-1.0.0b7-py3-none-any.whl && \
    pip install --no-cache-dir pytest==8.4.2 python-dotenv==1.1.1

EXPOSE 8088

CMD ["python", "main.py"]

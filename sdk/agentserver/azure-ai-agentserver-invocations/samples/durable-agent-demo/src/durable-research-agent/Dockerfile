FROM python:3.12-slim

WORKDIR /app

# Install local wheel packages first (built by build.sh before docker build)
COPY wheels/ /tmp/wheels/
RUN pip install --no-cache-dir /tmp/wheels/*.whl && rm -rf /tmp/wheels

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py agent.py supervisor.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Enable Task Storage API integration
ENV FOUNDRY_TASK_API_ENABLED=1
ENV STAGE_DURATION=5

EXPOSE 8088

# supervisor.py is PID 1: keeps /readiness alive, proxies to app, restarts on crash
CMD ["python", "supervisor.py"]


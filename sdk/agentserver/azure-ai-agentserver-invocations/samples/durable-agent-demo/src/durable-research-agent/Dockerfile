FROM python:3.12-slim

WORKDIR /app

# Install local wheel packages first (built by build.sh before docker build)
COPY wheels/ /tmp/wheels/
RUN pip install --no-cache-dir /tmp/wheels/*.whl && rm -rf /tmp/wheels

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py agent.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Use local file-based durability (persisted on disk within the sandbox)
ENV FOUNDRY_TASK_API_ENABLED=0
ENV STAGE_DURATION=10

EXPOSE 8088

# entrypoint.sh auto-restarts the agent on crash (the platform doesn't today)
CMD ["./entrypoint.sh"]


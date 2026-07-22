FROM python:3.12-slim

WORKDIR /app

# Install local wheel packages first (built by ../../build.sh before docker build).
# Bundles all three preview packages: core (resilient-task primitive),
# invocations (HTTP host), responses (OpenAI Responses API host).
COPY wheels/ /tmp/wheels/
RUN pip install --no-cache-dir /tmp/wheels/*.whl && rm -rf /tmp/wheels

# Install remaining dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY _task_trace.py ./

EXPOSE 8088

# This is a demo image — enables the "crash" sentinel handling in main.py.
# A production image would leave this off (default).
ENV DEMO_MODE=1

# Platform nanny worker handles restart on crash; we just run the agent.
CMD ["python", "main.py"]

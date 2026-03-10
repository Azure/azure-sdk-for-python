FROM python:3.12-slim

WORKDIR /app

# Install the agentserver package from the local source tree
COPY sdk/agentserver/azure-ai-agentserver /src/azure-ai-agentserver
RUN pip install --no-cache-dir /src/azure-ai-agentserver

# Copy the sample agent
COPY sdk/agentserver/azure-ai-agentserver/samples/simple_invoke_agent/simple_invoke_agent.py .

EXPOSE 8088

# Bind to 0.0.0.0 so the port is accessible from outside the container.
# The default is 127.0.0.1 which is only reachable inside the container.
CMD ["python", "-c", "\
from simple_invoke_agent import server; \
server.run(host='0.0.0.0') \
"]

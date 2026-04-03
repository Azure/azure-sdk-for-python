FROM python:3.11-slim

WORKDIR /app

# Install git (needed for some pip dependencies)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install new agentserver packages from pre-downloaded wheels
COPY _wheels/ /tmp/wheels/
RUN pip install --no-cache-dir /tmp/wheels/*.whl && rm -rf /tmp/wheels

# Copy the package source for local install (not on PyPI yet)
COPY _package/ /tmp/azure-ai-agentserver-githubcopilot/

# Copy the test agent
COPY . /app/

# Install the package from local source + agent deps
RUN pip install --no-cache-dir --pre /tmp/azure-ai-agentserver-githubcopilot/ -r requirements.txt && \
    rm -rf /tmp/azure-ai-agentserver-githubcopilot/

EXPOSE 8088

# ADC vNext: Append the egress proxy CA cert so outbound HTTPS works.
CMD bash -c '\
  if [ -f /etc/ssl/certs/adc-egress-proxy-ca.crt ]; then \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> /etc/ssl/certs/ca-certificates.crt && \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> $(python -c "import certifi; print(certifi.where())"); \
  fi && \
  python main.py'

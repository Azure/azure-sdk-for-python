FROM mcr.microsoft.com/mirror/docker/library/python:3.11-slim

WORKDIR /app

# Install git (needed for some pip dependencies)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install base packages from Azure DevOps feed FIRST (separate pip call
# to avoid the feed interfering with github-copilot-sdk from PyPI).
# Uses --index-url to satisfy CFS supply-chain policy.
RUN pip install --no-cache-dir --no-input --pre \
    --index-url https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/ \
    "azure-ai-agentserver-core>=2.0.0a1" \
    "azure-ai-agentserver-responses>=1.0.0a1"

# Copy the package source for local install (not on PyPI yet)
COPY _package/ /tmp/azure-ai-agentserver-githubcopilot/

# Copy the test agent
COPY . /app/

# Install the package from local source + agent deps (PyPI only — no dev feed).
RUN pip install --no-cache-dir --pre \
    /tmp/azure-ai-agentserver-githubcopilot/ \
    -r requirements.txt && \
    rm -rf /tmp/azure-ai-agentserver-githubcopilot/

EXPOSE 8088

# ADC vNext: Append the egress proxy CA cert so outbound HTTPS works.
CMD bash -c '\
  if [ -f /etc/ssl/certs/adc-egress-proxy-ca.crt ]; then \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> /etc/ssl/certs/ca-certificates.crt && \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> $(python -c "import certifi; print(certifi.where())"); \
  fi && \
  python main.py'

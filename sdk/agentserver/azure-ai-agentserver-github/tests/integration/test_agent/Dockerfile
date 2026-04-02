FROM mcr.microsoft.com/mirror/docker/library/python:3.11-slim

WORKDIR /app

# Copy the package source for local install (not on PyPI yet)
COPY _package/ /tmp/azure-ai-agentserver-github/

# Copy the test agent
COPY . /app/

# Install the package from local source + agent deps
RUN pip install --pre /tmp/azure-ai-agentserver-github/ -r requirements.txt && \
    rm -rf /tmp/azure-ai-agentserver-github/

EXPOSE 8088

# ADC vNext: Append the egress proxy CA cert so outbound HTTPS works.
CMD bash -c '\
  if [ -f /etc/ssl/certs/adc-egress-proxy-ca.crt ]; then \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> /etc/ssl/certs/ca-certificates.crt && \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> $(python -c "import certifi; print(certifi.where())"); \
  fi && \
  python main.py'

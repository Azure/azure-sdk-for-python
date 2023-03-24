import os
from pathlib import Path
from subprocess import getoutput


def add_certificate():
    # Set the following certificate paths:
    #     SSL_CERT_DIR=C:\<YOUR DIRECTORY>\azure-sdk-for-python\.certificate
    #     REQUESTS_CA_BUNDLE=C:\<YOUR DIRECTORY>\azure-sdk-for-python\.certificate\dotnet-devcert.pem
    result = getoutput(f"python {Path('scripts/devops_tasks/trust_proxy_cert.py')}").split("\n")
    for item in result[1:]:
        name, value = item.strip().split("=", 1)
        os.environ[name] = value
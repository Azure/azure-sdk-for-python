# Azure Identity client library for Python

# Getting started

# Key concepts

# Examples
Authenticating as a service principal:
```py
# using a client secret
from azure.identity import ClientSecretCredential
credential = ClientSecretCredential(client_id, secret, tenant_id)

# all credentials implement get_token
token = credential.get_token(scopes=["https://vault.azure.net/.default"])

# using a certificate requires a thumbprint and PEM-encoded private key
from azure.identity import CertificateCredential
with open("private-key.pem") as f:
    private_key = f.read()
credential = CertificateCredential(client_id, tenant_id, private_key, thumbprint)
```

Authenticating via environment variables:
```py
from azure.identity import EnvironmentCredential

# will authenticate with client secret or certificate,
# depending on which environment variables are set
# (see constants.py for expected variable names)
credential = EnvironmentCredential()
token = credential.get_token(scopes=["https://vault.azure.net/.default"])
```

Chaining together multiple credentials:
```py
from azure.identity import TokenCredentialChain

# default credentials are environment then managed identity
credential_chain = TokenCredentialChain.default()

scopes = ["https://vault.azure.net/.default"]
# the chain has a get_token method like all credentials
token = credential_chain.get_token(scopes)  # try each credential in order, return the first token
```

Authenticating from a service client:
```py
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

credential_chain = TokenCredentialChain.default()
scopes = ["https://vault.azure.net/.default"]

# BearerTokenCredentialPolicy gets tokens as necessary, adds appropriate auth headers to requests
policies = [BearerTokenCredentialPolicy(credential=credential_chain, scopes=scopes)]
pipeline = Pipeline(transport=some_transport, policies=policies)
```
# Troubleshooting

# Next steps

# Contributing

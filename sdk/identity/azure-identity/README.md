# Azure Identity client library for Python

# Getting started

# Key concepts

# Examples
Shortest path to an access token:
```py
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(client_id, secret, tenant_id)

# all credentials implement get_token
token = credential.get_token(scopes=["https://vault.azure.net/.default"])
```

# Troubleshooting

# Next steps

# Contributing

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from dotenv import load_dotenv

from azure.identity import ClientSecretCredential
from azure.keyvault.certificates import CertificateClient
from azure.keyvault.keys import KeyClient
from azure.keyvault.secrets import SecretClient

load_dotenv()

if "AZURE_KEYVAULT_URL" not in os.environ:
    raise EnvironmentError("Missing a Key Vault URL")
if "KEYVAULT_TENANT_ID" not in os.environ:
    raise EnvironmentError("Missing a tenant ID for Key Vault")
if "KEYVAULT_CLIENT_ID" not in os.environ:
    raise EnvironmentError("Missing a client ID for Key Vault")
if "KEYVAULT_CLIENT_SECRET" not in os.environ:
    raise EnvironmentError("Missing a client secret for Key Vault")

credential = ClientSecretCredential(
    tenant_id=os.environ["KEYVAULT_TENANT_ID"],
    client_id=os.environ["KEYVAULT_CLIENT_ID"],
    client_secret=os.environ["KEYVAULT_CLIENT_SECRET"]
)

cert_client = CertificateClient(os.environ["AZURE_KEYVAULT_URL"], credential)
key_client = KeyClient(os.environ["AZURE_KEYVAULT_URL"], credential)
secret_client = SecretClient(os.environ["AZURE_KEYVAULT_URL"], credential)

test_certificates = [c for c in cert_client.list_properties_of_certificates() if c.name.startswith("livekvtest")]
for certificate in test_certificates:
    cert_client.begin_delete_certificate(certificate.name).wait()
deleted_test_certificates = [
    c for c in cert_client.list_deleted_certificates(include_pending=True) if c.name.startswith("livekvtest")
]
for certificate in deleted_test_certificates:
    cert_client.purge_deleted_certificate(certificate.name)

test_keys = [k for k in key_client.list_properties_of_keys() if k.name.startswith("livekvtest")]
for key in test_keys:
    key_client.begin_delete_key(key.name).wait()
deleted_test_keys = [k for k in key_client.list_deleted_keys() if k.name.startswith("livekvtest")]
for key in deleted_test_keys:
    key_client.purge_deleted_key(key.name)

test_secrets = [s for s in secret_client.list_properties_of_secrets() if s.name.startswith("livekvtest")]
for secret in test_secrets:
    secret_client.begin_delete_secret(secret.name).wait()
deleted_test_secrets = [s for s in secret_client.list_deleted_secrets() if s.name.startswith("livekvtest")]
for secret in deleted_test_secrets:
    secret_client.purge_deleted_secret(secret.name)

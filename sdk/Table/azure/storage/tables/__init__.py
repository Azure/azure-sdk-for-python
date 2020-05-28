__all__ = [
    'generate_account_sas',
]

from azure.storage.tables._shared.shared_access_signature import generate_account_sas
from azure.storage.tables._table_service_client import TableServiceClient
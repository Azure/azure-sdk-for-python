"""
Azure Communication Services SMS SDK for Python (Async).

Recommended Usage (Hierarchical Client Pattern):
    from azure.communication.sms.aio import SmsClient
    
    sms_client = SmsClient.from_connection_string(connection_string)
    opt_outs_client = sms_client.get_opt_outs_client()  # Preferred approach
"""

from ._sms_client_async import SmsClient
from ._opt_outs_client_async import OptOutsClient

__all__ = [
    "SmsClient",
    "OptOutsClient",  # Still exposed for backward compatibility
]

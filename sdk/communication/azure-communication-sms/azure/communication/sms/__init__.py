"""
Azure Communication Services SMS SDK for Python.

This SDK provides SMS messaging capabilities for Azure Communication Services.

Recommended Usage (Hierarchical Client Pattern):
    from azure.communication.sms import SmsClient
    
    sms_client = SmsClient.from_connection_string(connection_string)
    opt_outs_client = sms_client.get_opt_outs_client()  # Preferred approach

Alternative Usage (Direct Client Access):
    from azure.communication.sms import SmsClient, OptOutsClient
    
    sms_client = SmsClient.from_connection_string(connection_string)
    opt_outs_client = OptOutsClient.from_connection_string(connection_string)
    
Note: The hierarchical pattern (SmsClient.get_opt_outs_client()) is recommended
as it follows Azure SDK Design Guidelines and provides better consistency with
other Azure services.
"""

from ._sms_client import SmsClient
from ._opt_outs_client import OptOutsClient

from ._models import SmsSendResult, OptOutResult, OptOutCheckResult

__all__ = [
    "SmsClient",
    "OptOutsClient",  # Exposed for direct access (alternative to hierarchical pattern)
    "SmsSendResult",
    "OptOutResult",
    "OptOutCheckResult",
]

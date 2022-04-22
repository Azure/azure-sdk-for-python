#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, List, Optional

from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import TokenCredential

from ._generated._monitor_ingestion_client import MonitorIngestionClient
from ._helpers import get_authentication_policy

class LogsIngestionClient(object):
    """Azure Monitor Ingestion Python Client.

    :param endpoint: The Data Collection Endpoint for the Data Collection Rule, for example
     https://dce-name.eastus-2.ingest.monitor.azure.com.
    :type endpoint: str
    :keyword api_version: Api Version. Default value is "2021-11-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(self,
        endpoint: str,
        credential: TokenCredential,
        *,
        api_version: str,
        **kwargs: Any
        ):
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._client = MonitorIngestionClient(
            credential=credential,
            authentication_policy=get_authentication_policy(credential, endpoint),
            base_url=self._endpoint.rstrip('/'),
            api_version=api_version,
            **kwargs
        )
        self._client = self._client.data_collection_rule

    @distributed_trace
    def ingest(
        self,
        rule_id: str,
        stream: str,
        body: List[Any],
        content_encoding: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Ingestion API used to directly ingest data using Data Collection Rules.

        See error response code and error response message for more detail.

        :param rule_id: The immutable Id of the Data Collection Rule resource.
        :type rule_id: str
        :param stream: The streamDeclaration name as defined in the Data Collection Rule.
        :type stream: str
        :param body: An array of objects matching the schema defined by the provided stream.
        :type body: list[any]
        :param content_encoding: gzip. Default value is None.
        :type content_encoding: str
        :keyword str x_ms_client_request_id: Client request Id. Default value is None.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.ingest(
            rule_id=rule_id,
            stream=stream,
            body=body,
            content_encoding=content_encoding,
            **kwargs
        )

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.monitor.ingestion.LogsIngestion` session."""
        return self._client.close()

    def __enter__(self):
        # type: () -> LogsIngestionClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member

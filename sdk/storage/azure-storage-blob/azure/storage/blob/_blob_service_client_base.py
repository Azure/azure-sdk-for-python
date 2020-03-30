# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, cast,
    TYPE_CHECKING
)

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from ._shared.base_client import StorageAccountHostsMixin, parse_query
from ._generated import AzureBlobStorage, VERSION
from ._serialize import get_api_version

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from ._shared.models import UserDelegationKey
    from ._lease import BlobLeaseClient
    from ._models import (
        BlobProperties,
        ContainerProperties,
        PublicAccess,
        BlobAnalyticsLogging,
        Metrics,
        CorsRule,
        RetentionPolicy,
        StaticWebsite,
    )


class BlobServiceClientBase(StorageAccountHostsMixin):
    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        _, sas_token = parse_query(parsed_url.query)
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(BlobServiceClientBase, self).__init__(parsed_url, service='blob', credential=credential, **kwargs)
        self._client = AzureBlobStorage(self.url, pipeline=self._pipeline)
        self._client._config.version = get_api_version(kwargs, VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}/{}".format(self.scheme, hostname, self._query_str)

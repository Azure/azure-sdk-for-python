# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, TYPE_CHECKING

from azure.core import PipelineClient
from azure.core.pipeline import Pipeline

from ._client import DataLakeClient as GeneratedDataLakeClient
from ._configuration import DataLakeClientConfiguration as GeneratedDataLakeClientConfiguration
from .._shared.policies import RangeHeaderPolicy

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class DataLakeClientConfiguration(GeneratedDataLakeClientConfiguration):
    """Configuration for DataLakeClient that allows optional credentials.

    Overrides the generated configuration to allow None credentials
    for anonymous access.
    """

    def __init__(self, url: str, credential: Optional["TokenCredential"] = None, **kwargs: Any) -> None:
        if url is None:
            raise ValueError("Parameter 'url' must not be None.")
        version: str = kwargs.pop("version", "2026-06-06")
        self.url = url
        self.credential = credential
        self.version = version
        self.credential_scopes = kwargs.pop("credential_scopes", ["https://storage.azure.com/.default"])
        from ._version import VERSION

        kwargs.setdefault("sdk_moniker", "storage-file-datalake/{}".format(VERSION))
        self.polling_interval = kwargs.get("polling_interval", 30)
        self._configure(**kwargs)


class DataLakeClient(GeneratedDataLakeClient):
    """Subclass of the generated DataLakeClient that allows optional credentials,
    accepts a pre-built pipeline, and injects the RangeHeaderPolicy.
    """

    def __init__(
        self, url: str, credential: Optional["TokenCredential"] = None, *, pipeline: Any = None, **kwargs: Any
    ) -> None:
        from ._utils.serialization import Deserializer, Serializer
        from .operations import FileSystemOperations, PathOperations, ServiceOperations

        if pipeline is None:
            raise ValueError("Parameter 'pipeline' must not be None.")

        _endpoint = "{url}"
        self._config = DataLakeClientConfiguration(url=url, credential=credential, **kwargs)
        impl_policies = list(pipeline._impl_policies)  # pylint: disable=protected-access
        has_range_header_policy = any(
            isinstance(getattr(policy, "_policy", policy), RangeHeaderPolicy)  # pylint: disable=protected-access
            for policy in impl_policies
        )
        if not has_range_header_policy:
            impl_policies.insert(0, RangeHeaderPolicy())
        self._client = PipelineClient(
            base_url=_endpoint,
            pipeline=Pipeline(
                transport=pipeline._transport,  # pylint: disable=protected-access
                policies=impl_policies,
            ),
        )

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False
        self.service = ServiceOperations(self._client, self._config, self._serialize, self._deserialize)
        self.file_system = FileSystemOperations(self._client, self._config, self._serialize, self._deserialize)
        self.path = PathOperations(self._client, self._config, self._serialize, self._deserialize)


__all__: list[str] = ["DataLakeClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

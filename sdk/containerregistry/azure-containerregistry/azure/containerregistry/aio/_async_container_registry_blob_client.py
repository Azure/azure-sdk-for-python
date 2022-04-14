# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.tracing.decorator_async import distributed_trace_async

from ._async_base_client import ContainerRegistryBaseClient
from .._helpers import SUPPORTED_API_VERSIONS, OCI_MANIFEST_MEDIA_TYPE, _is_tag, _serialize_manifest, _compute_digest
from .._container_registry_blob_client import _return_response

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from typing import Any, Optional, IO
    from .._generated.models import OCIManifest, ManifestWrapper


class ContainerRegistryBlobClient(ContainerRegistryBaseClient):
    def __init__(
        self, endpoint: str, credential: Optional["AsyncTokenCredential"] = None, *, audience, **kwargs: Any) -> None:
        """Create a ContainerRegistryClient from an ACR endpoint and a credential.

        :param str endpoint: An ACR endpoint.
        :param credential: The credential with which to authenticate.
        :type credential: ~azure.core.credentials_async.AsyncTokenCredential
        :keyword api_version: API Version. The default value is "2021-07-01". Note that overriding this default value
         may result in unsupported behavior.
        :paramtype api_version: str
        :keyword audience: URL to use for credential authentication with AAD. Its value could be
         "https://management.azure.com", "https://management.chinacloudapi.cn", "https://management.microsoftazure.de"
         or "https://management.usgovcloudapi.net".
        :paramtype audience: str
        :returns: None
        :rtype: None
        :raises ValueError: If the provided api_version keyword-only argument isn't supported or
         audience keyword-only argument isn't provided.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_hello_world_async.py
                :start-after: [START create_registry_client]
                :end-before: [END create_registry_client]
                :language: python
                :dedent: 8
                :caption: Instantiate an instance of `ContainerRegistryClient`
        """
        api_version = kwargs.get("api_version", None)
        if api_version and api_version not in SUPPORTED_API_VERSIONS:
            supported_versions = "\n".join(SUPPORTED_API_VERSIONS)
            raise ValueError(
                "Unsupported API version '{}'. Please select from:\n{}".format(
                    api_version, supported_versions
                )
            )
        defaultScope = [audience + "/.default"]
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        super(ContainerRegistryBlobClient, self).__init__(
            endpoint=endpoint, credential=credential, credential_scopes=defaultScope, **kwargs)
    
    @distributed_trace_async
    async def upload_manifest(self, repository: str, manifest: OCIManifest, *, tag: Optional[str]=None, **kwargs: "Any"):
        """Upload a manifest for an OCI artifact.

        :param str repository: Name of the repository
        :param manifest: The manifest to upload.
        :type manifest: ~azure.containerregistry.models.OCIManifest
        :keyword tag: Tag of the manifest.
        :paramtype tag: str
        :returns: None
        :rtype: None
        """       
        tag_or_digest = tag
        if tag:
            stream = _serialize_manifest(manifest)
            tag_or_digest = _compute_digest(stream)
        await self._client.container_registry.create_manifest(
            repository, tag_or_digest, stream, content_type=OCI_MANIFEST_MEDIA_TYPE, **kwargs)
        
    @distributed_trace_async
    async def upload_manifest(self, repository: str, stream: IO, *, tag: Optional[str]=None, **kwargs: "Any"):
        """Upload a manifest for an OCI artifact.

        :param str repository: Name of the repository
        :param stream: The manifest to upload.
        :type stream: IO
        :keyword tag: Tag of the manifest.
        :paramtype tag: str
        :returns: None
        :rtype: None
        """
        tag_or_digest = tag
        if tag:
            tag_or_digest = _compute_digest(stream)
        await self._client.container_registry.create_manifest(
            repository, tag_or_digest, stream, content_type=OCI_MANIFEST_MEDIA_TYPE, **kwargs)
        
    @distributed_trace_async
    async def upload_blob(self, repository, stream, **kwargs):
        # type: (str, IO, **Any) -> None
        """Upload an artifact blob.

        :param str repository: Name of the repository
        :param stream: The manifest to upload.
        :type stream: IO
        :returns: None
        :rtype: None
        """
        start_upload_response = await self._client.container_registry_blob.start_upload(
            repository, cls=_return_response, **kwargs)
        upload_chunk_response = await self._client.container_registry_blob.upload_chunk(
            start_upload_response['Location'], stream, cls=_return_response, **kwargs)
        digest = _compute_digest(stream)
        await self._client.container_registry_blob.complete_upload(
            digest, upload_chunk_response['Location'], stream, cls=_return_response, **kwargs)
        
    @distributed_trace_async
    async def download_manifest(self, repository, tag_or_digest, **kwargs):
        # type: (str, str, **Any) -> ManifestWrapper
        """Download the manifest for an OCI artifact.

        :param str repository: Name of the repository
        :param str tag_or_digest: The manifest to upload.
        :returns: ManifestWrapper
        :rtype: ~container_registry.models.ManifestWrapper
        """
        return await self._client.container_registry.get_manifest(
            repository, tag_or_digest, OCI_MANIFEST_MEDIA_TYPE, **kwargs)
    
    @distributed_trace_async
    async def download_blob(self, repository, digest, **kwargs):
        # type: (str, str, **Any) -> IO | None
        """Download a blob that is part of an artifact.

        :param str repository: Name of the repository
        :param str digest: The digest of the blob to download.
        :returns: IO or None
        :rtype: IO or None
        """
        return await self._client.container_registry_blob.get_blob(repository, digest, **kwargs)
    
    @distributed_trace_async
    async def delete_blob(self, repository, tag_or_digest, **kwargs):
        # type: (str, str, **Any) -> IO
        """Delete a blob. If the blob cannot be found or a response status code of
        404 is returned an error will not be raised.

        :param str repository: Name of the repository the manifest belongs to
        :param str tag_or_digest: Tag or digest of the blob to be deleted
        :returns: IO
        :rtype: IO
        :raises: ~azure.core.exceptions.HttpResponseError

        Example

        .. code-block:: python

            from azure.containerregistry import ContainerRegistryClient
            from azure.identity import DefaultAzureCredential
            endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]
            client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="my_audience")
            response = await client.delete_blob("my_repository", "my_tag_or_digest")
        """
        if _is_tag(tag_or_digest):
            tag_or_digest = self._get_digest_from_tag(repository, tag_or_digest)

        return await self._client.container_registry_blob.delete_blob(repository, tag_or_digest, **kwargs)

    
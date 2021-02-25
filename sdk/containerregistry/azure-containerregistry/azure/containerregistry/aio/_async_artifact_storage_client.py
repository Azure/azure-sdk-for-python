# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


class ArtifactStorageClient(object):
    def __init__(
        self, endpoint: str, repository_name: str, credential: TokenCredential, **kwargs
    ) -> None:
        pass

    def cancel_upload(self, location: str, **kwargs) -> None:
        pass

    def check_blob_exists(self, digest: str, **kwargs) -> bool:
        pass

    def check_chunk_exists(self, digest: str, range: HttpRange, **kwargs) -> bool:
        pass

    def complete_upload(
        self, upload_details: CreateUploadResult, digest: str, value: Stream = None, **kwargs
    ) -> None:
        pass

    def create_manifest(self, manifest: ArtifactManifest, tag: str = None, **kwargs) -> None:
        pass

    def create_upload(self, **kwargs) -> CreateUploadResult:
        pass

    def delete(self, **kwargs) -> None:
        pass

    def delete_blob(self, digest: str, **kwargs) -> Stream:
        pass

    def get_blob(self, digest: str, **kwargs) -> Stream:
        pass

    def get_chunk(self, digest: str, range: HttpRange, **kwargs) -> Stream:
        pass

    def get_manifest(
        self, tag_or_digest: str, accept_media_types: list[ManifestMediaType] = None, **kwargs
    ) -> ArtifactManifest:
        pass

    def get_upload_status(self, location: str, **kwargs) -> Response:
        pass

    def mount_blob(self, blob_from: str, mount: str, **kwargs) -> Response:
        pass

    def upload_chunk(
        self, upload_details: CreateUploadResult, value: Stream, **kwargs
    ) -> CreateUploadResult:
        pass

# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


class ArtifactStorageClient(object):
    def __init__(self, endpoint, repository, credential):
        # type: (str, str, TokenCredential) -> None
        pass

    def cancel_upload(self, location, **kwargs):
        # type: (str) -> None
        pass

    def check_blob_exists(self, digest, **kwargs):
        # type: (str) -> bool
        pass

    def check_chunk_exists(self, digest, range, **kwargs):
        # type: (str, HttpRange) -> bool
        pass

    def complete_upload(self, upload_details, digest, value=None, **kwargs):
        # type: (CreateUploadResult, str, Stream) -> None
        pass

    def create_manifest(self, manifest, tag=None, **kwargs):
        # type: (ArtifactManifest, str) -> None
        pass

    def create_upload(self, **kwargs):
        # type: (...) -> CreateUploadResult
        pass

    def delete(self, **kwargs):
        # type: (...) -> None
        pass

    def delete_blob(self, digest, **kwargs):
        # type: (str) -> Stream
        pass

    def get_blob(self, digest, **kwargs):
        # type: (str) -> Stream
        pass

    def get_chunk(self, digest, range, **kwargs):
        # type: (str, HttpRange) -> Stream
        pass

    def get_manifest(self, tag_or_digest, accept_media_types=None, **kwargs):
        # type: (str, Optional[List[ManifestMediaType]]) -> ArtifactManifest
        pass

    def get_upload_status(self, location, **kwargs):
        # type: (str) -> Response
        pass

    def mount_blob(self, blob_from, mount, **kwargs):
        # type: (str, str) -> Response
        pass

    def upload_chunk(self, upload_details, value, **kwargs):
        # type: (CreateUploadResult, Stream) -> CreateUploadResult
        # TODO: upload_details should prob be a different type than the returned one
        pass

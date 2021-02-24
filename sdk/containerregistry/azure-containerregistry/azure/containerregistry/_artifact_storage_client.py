# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

class ArtifactClient(object):

    def __init__(self, endpoint, repository_name, credential):
        # type: (str, str, TokenCredential) -> None
        pass

    def cancel_upload(self, location):
        # type: (str) -> None
        pass

    def check_blob_exists(self, digest):
        # type: (str) -> bool
        pass

    def check_chunk_exists(self, digest, range):
        # type: (str, HttpRange) -> bool
        pass

    def complete_upload(self, upload_details, digest, value=None):
        # type: (CreateUploadResult, str, Stream) -> None
        pass

    def create_manifest(self, manifest, tag=None):
        # type: (ArtifactManifest, str) -> None
        pass

    def create_upload(self):
        # type: (...) -> CreateUploadResult
        pass

    def delete(self):
        # type: (...) -> None

    def delete_blob(self, digest):
        # type: (str) -> Stream
        pass

    def get_blob(self, digest):
        # type: (str) -> Stream
        pass

    def get_chunk(self, digest, range):
        # type: (str, HttpRange) -> Stream
        pass

    def get_manifest(self, tag_or_digest, accept_media_types=None):
        # type: (str, Optional[List[ManifestMediaType]]) -> ArtifactManifest
        pass

    def get_upload_status(self, location):
        # type: (str) -> Response
        pass

    def mount_blob(self, blob_from, mount):
        # type: (str, str) -> Response
        pass

    def upload_chunk(self, upload_details, value):
        # type: (CreateUploadResult, Stream) -> CreateUploadResult
        # TODO: upload_details should prob be a different type than the returned one
        pass

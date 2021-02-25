# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

class ArtifactManifest(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.media_type = kwargs.get('media_type', None)
        self.schema_version = kwargs.get('media_version', None)

    def as_docker_manifest_list(self):
        # type: (...) -> DockerManifestList
        pass

    def as_docker_manifest_v1(self):
        # type: (...) -> DockerManifestV1
        pass

    def as_docker_manifest_v2(self):
        # type: (...) -> DockerManifestV2
        pass

    def as_docker_manifest_v1(self):
        # type: (...) -> DockerManifestV1
        pass

    def as_oci_index(self):
        # type: (...) -> OCIIndex
        pass

    def as_oci_manifest(self):
        # type: (...) -> OCIManifest
        pass


class CompleteUploadResult(object):

    def __init__(self, digest, location, http_range):
        # type: (str, str, HttpRange)
        self.digest = digest
        self.location = location
        self.http_range = http_range


class ConfigMediaType(object):

    def __init__(self):
        self.docker_image_v1 = None
        self.oci_image_config = None
        pass

    def __eq__(self, right):
        # type: (ConfigMediaType) -> bool
        pass

    def __ne__(self, right):
        # type: (ConfigMediaType) -> bool
        return not self.__eq__(right)

    def get_has_code(self):
        # type: (...) -> int
        pass

    def __repr__(self):
        # type: (...) -> str
        pass


class ContentDescriptor(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.media_type = kwargs.get('media_type', None)
        self.annotations = kwargs.get('annotations', None)
        self.digest = kwargs.get('digest', None)
        self.size = kwargs.get('size', None)
        self.urls = kwargs.get('urls', None)
        self.compute_digest = kwargs.get('compute_digest', None)

    @classmethod
    def _from_generated(self, generated):
        # type: (Generated) -> ContentDescriptor
        pass


class CreateManifestResult(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.content_length = kwargs.get('content_length', None)
        self.digest = kwargs.get('digest', None)
        self.location = kwargs.get('location', None)

    @classmethod
    def _from_generated(self, generated):
        # type: (Generated) -> CreateManifestResult
        pass


class CreateUploadResult(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.location = kwargs.get('location', None)
        self.http_range = kwargs.get('http_range', None)
        self.upload_id = kwargs.get('upload_id', None)

    @classmethod
    def _from_generated(self, generated):
        # type: (Generated) -> CreateUploadResult
        pass


# NOTE: This might be unnecessary, Pageable[ArtifactManifest]
class DockerManifestList(ArtifactManifest):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.manifests = kwargs.get('manifests', None)


class DockerManifestV1(ArtifactManifest):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.architecture = kwargs.get('architecture', None)
        self.fs_layers = kwargs.get('fs_layers', None)
        self.history = kwargs.get('history', None)
        self.name = kwargs.get('name', None)
        self.signatures = kwargs.get('signatures', None)
        self.tag = kwargs.get('tag', None)


class DockerManifestV1FsLayer(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.blob_sum = kwargs.get('blob_sum', None)


class DockerManifestV1History(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.v1_compatibility = kwargs.get('v1_compatibility', None)


class DockerManifestV1ImageHistory(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.header = kwargs.get('header', None)
        self.protected = kwargs.get('protected', None)
        self.signature = kwargs.get('signature', None)


class DockerManifestV1Jwk(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.alg = kwargs.get('alg', None)
        self.jwk = kwargs.get('jwk', None)


class DockerManifestV1JwkHeader(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.crv = kwargs.get('crv', None)
        self.kid = kwargs.get('kid', None)
        self.kty = kwargs.get('kty', None)
        self.x = kwargs.get('x', None)
        self.y = kwargs.get('y', None)


class DockerManifestV2(ArtifactManifest):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.config_descriptor = kwargs.get('config_descriptor')
        self.layers = kwargs.get('layers')

    @classmethod
    def from_stream(self, stream):
        # type: (Stream) -> DockerManifestV2
        pass

class ManifestListAttributes(object):

    def __init__(self, **kwargs):
        # type: (...) -> None
        self.digest = kwargs.get('digest', None)
        self.media_type = kwargs.get('media_type', None)
        self.platform = kwargs.get('platform', None)
        self.size = kwargs.get('size', None)


class ManifestMediaType(object):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        pass

    def __eq__(self, other):
        # type: (ManifestMediaType) -> bool
        pass

    def __ne__(self, other):
        # type: (ManifestMediaType) -> bool
        return not self.__eq__(other)

    def __repr__(self):
        # type: (...) -> str
        pass

    def get_hash_code(self):
        # type: (...) -> int
        pass


class OCIIndex(ArtifactManifest):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.annotations = kwargs.get('annotations', None)
        self.manifests = kwargs.get('manifests', None)


class OCIManifest(ArtifactManifest):

    def __init__(self, **kwargs):
        # type: (Optional[Dict[str, Any]]) -> None
        self.annotations = kwargs.get('annotations', None)
        self.config_descriptor = kwargs.get('config_descriptos', None)
        self.layers = kwargs.get('layers', None)


# NOTE: This might not be needed, could return just a dict
class OCIManifestAnnotations(dict):

    def __init__(self):
        # type: (...) -> None
        pass


class RuntimePlatform(object):

    def __init__(self):
        # type: (...) -> None
        pass


class UploadStatus(object):

    def __init__(self):
        self.http_range = kwargs.get('http_range', None)
        self.upload_id = kwargs.get('upload_id', None)
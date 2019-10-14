# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines


from azure.storage.blob import ContainerProperties, LeaseProperties, ContentSettings, ContainerSasPermissions, \
    BlobSasPermissions, AccessPolicy, ContainerPropertiesPaged, BlobProperties, BlobPropertiesPaged


class FileSystemProperties(ContainerProperties):
    def __init__(self, **kwargs):
        super(FileSystemProperties, self).__init__(
            **kwargs
        )


class ContainerPropertiesPaged(ContainerPropertiesPaged):
    def __init__(self, **kwargs):
        super(ContainerPropertiesPaged, self).__init__(
            **kwargs
        )


class PathProperties(BlobProperties):
    def __init__(self, **kwargs):
        super(PathProperties, self).__init__(
            **kwargs
        )


class PathPropertiesPaged(BlobPropertiesPaged):
    def __init__(self, **kwargs):
        super(PathPropertiesPaged, self).__init__(
            **kwargs
        )


class LeaseProperties(LeaseProperties):
    def __init__(self, **kwargs):
        super(LeaseProperties, self).__init__(
            **kwargs
        )


class ContentSettings(ContentSettings):
    def __init__(
            self, content_type=None, content_encoding=None,
            content_language=None, content_disposition=None,
            cache_control=None, content_md5=None, **kwargs):
        super(ContentSettings, self).__init__(
            content_type=content_type,
            content_encoding=content_encoding,
            content_language=content_language,
            content_disposition=content_disposition,
            cache_control=cache_control,
            content_md5=content_md5,
            **kwargs
        )


class AccessPolicy(AccessPolicy):
    def __init__(self, permission=None, expiry=None, start=None):
        super(AccessPolicy, self).__init__(
            start=start,
            expiry=expiry,
            permission=permission
        )


class FileSystemSasPermissions(ContainerSasPermissions):
    def __init__(self, **kwargs):
        super(FileSystemSasPermissions, self).__init__(
            **kwargs
        )


class PathSasPermissions(BlobSasPermissions):
    def __init__(self, **kwargs):
        super(PathSasPermissions, self).__init__(
            **kwargs
        )

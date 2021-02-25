# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum

from ._generated.models import (
    DeletedRepository,
)


class AzureAdminUserCredential(object):
    def __init__(self, username, password, **kwargs):
        # type: (str, str) -> None
        self.username = username
        self.password = password

    def update_password(self, password, **kwargs):
        # type: (str) -> None
        self.password = password


class ContentPermissions(object):
    def __init__(self, **kwargs):
        self.delete = kwargs.get("delete")
        self.list = kwargs.get("list")
        self.read = kwargs.get("read")
        self.write = kwargs.get("write")


class DeletedRepositoryResult(DeletedRepository):
    def __init__(self, **kwargs):
        super(DeletedRepositoryResult, self).__init__(**kwargs)
        pass


class GetManifestOptions(object):
    def __init__(self, **kwargs):
        pass


class GetTagOptions(object):
    def __init__(self, **kwargs):
        pass


class ArtifactAttributes(object):
    def __init__(self, **kwargs):
        pass


class ManifestOrderBy(int, Enum):

    LastUpdateTimeDescending = 0
    LastUpdateTimeAscending = 1


class RepositoryAttributes(object):
    def __init__(self, **kwargs):
        pass


class TagAttributes(object):
    def __init__(self, **kwargs):
        pass


class TagOrderBy(int, Enum):

    LastUpdateTimeDescending = 0
    LastUpdateTimeAscending = 1

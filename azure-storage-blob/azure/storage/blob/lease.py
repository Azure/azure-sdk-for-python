# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)

from ._utils import (
    get_modification_conditions,
    return_response_headers
)

if TYPE_CHECKING:
    from datetime import datetime
    from ._generated.operations import BlobOperations, ContainerOperations


class Lease(object):

    def __init__(self, client, **kwargs):
        # type: (Union[BlobOperations, ContainerOperations], **Any) -> None
        self.etag = kwargs.get('ETag')  # type: str
        self.id = kwargs.get('x-ms-lease-id')  # type: str
        self.last_modified = kwargs.get('Last-Modified')   # type: datetime 
        self._client = client

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()

    def renew(
            self, if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.aquire_lease(
            lease_id=self.id,
            timeout=timeout,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        self.etag = response.get('ETag')  # type: str
        self.id = response.get('x-ms-lease-id')  # type: str
        self.last_modified = response.get('Last-Modified')   # type: datetime 

    def release(
            self, if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.aquire_lease(
            lease_id=self.id,
            timeout=timeout,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        self.etag = response.get('ETag')  # type: str
        self.id = response.get('x-ms-lease-id')  # type: str
        self.last_modified = response.get('Last-Modified')   # type: datetime 

    def change(
            self, proposed_lease_id,  # type: str
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.aquire_lease(
            lease_id=self.id,
            proposed_lease_id=proposed_lease_id,
            timeout=timeout,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        self.etag = response.get('ETag')  # type: str
        self.id = response.get('x-ms-lease-id')  # type: str
        self.last_modified = response.get('Last-Modified')   # type: datetime 


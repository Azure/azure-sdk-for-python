# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import time

from azure.core.exceptions import AzureError
from azure.core.polling import PollingMethod, LROPoller


logger = logging.getLogger(__name__)


def finished(status):
    if hasattr(status, 'value'):
        status = status.value
    return str(status).lower() in ['success', 'aborted', 'failed']


def failed(status):
    if hasattr(status, 'value'):
        status = status.value
    return str(status).lower() in ['failed', 'aborted']


def succeeded(status):
    if hasattr(status, 'value'):
        status = status.value
    return str(status).lower() in ['success']


class CopyStatusPoller(LROPoller):

    def id(self):
        return self._polling_method.id

    def abort(self):
        return self._polling_method.abort()


class CopyBlob(PollingMethod):
    """An empty poller that returns the deserialized initial response.
    """
    def __init__(self, interval, **kwargs):
        self._client = None
        self._initial_response = None
        self._status = 'pending'
        self.id = None
        self.etag = None
        self.last_modified = None
        self.polling_interval = interval
        self.kwargs = kwargs
        self.blob = None

    def initialize(self, client, initial_response, _):
        # type: (Any, requests.Response, Callable) -> None
        self._client = client
        self._status = initial_response['x-ms-copy-status']
        self._initial_response = initial_response
        self.id = initial_response['x-ms-copy-id']
        self.etag = initial_response['ETag']
        self.last_modified = initial_response['Last-Modified']
        # if initial_response.get('x-ms-error-code'):
        #     raise Exception(initial_response['x-ms-error-code'])  # TODO

    def run(self):
        # type: () -> None
        """Empty run, no polling.
        """
        try:
            while not self.finished():
                self.blob = self._client.get_blob_properties(**self.kwargs)
                self._status = self.blob.copy.status
                self.etag = self.blob.etag
                self.last_modified = self.blob.last_modified
                time.sleep(self.polling_interval)
            if failed(self.status()):
                raise ValueError("Copy operation failed: {}".format(self.blob.copy.status_description))
        except Exception as e:
            logger.warning(str(e))

    def abort(self):
        if not self.finished():
            return self._client._client.blob.abort_copy_from_url(self.id, **self.kwargs)
        raise ValueError("Copy operation already complete.")

    def status(self):
        # type: () -> str
        """Return the current status as a string.
        :rtype: str
        """
        return self._status

    def finished(self):
        # type: () -> bool
        """Is this polling finished?
        :rtype: bool
        """
        return finished(self.status())

    def resource(self):
        # type: () -> Any
        if not self.blob:
            self.blob = self._client.get_blob_properties(**self.kwargs)
        return self.blob

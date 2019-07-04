# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import time
from typing import Callable, Any # pylint: disable=unused-import
from azure.core.polling import PollingMethod, LROPoller

from ._shared.utils import process_storage_error
from ._generated.models import StorageErrorException
from ._blob_utils import deserialize_blob_properties


logger = logging.getLogger(__name__)


class CopyStatusPoller(LROPoller):
    """Poller for a long-running copy operation."""

    def __init__(self, client, copy_id, polling=True, configuration=None, **kwargs):
        if configuration:
            polling_interval = configuration.blob_settings.copy_polling_interval
        else:
            polling_interval = 2
        polling_method = CopyBlobPolling if polling else CopyBlob
        poller = polling_method(polling_interval, **kwargs)
        super(CopyStatusPoller, self).__init__(client, copy_id, None, poller)

    def copy_id(self):
        # type: () -> str
        """Get the ID of the copy operation.

        :rtype: str
        """
        return self._polling_method.id

    def abort(self):
        # type: () -> None
        """Abort the copy operation.

        This will leave a destination blob with zero length and full metadata.
        This will raise an error if the copy operation has already ended.

        :rtype: None
        """
        return self._polling_method.abort()

    def status(self): # pylint: disable=useless-super-delegation
        # type: () -> str
        """Returns the current status of the copy operation.

        :rtype: str
        """
        return super(CopyStatusPoller, self).status()

    def result(self, timeout=None):
        # type: (Optional[int]) -> Model
        """Return the BlobProperties after the completion of the copy operation,
        or the properties available after the specified timeout.

        :returns: The destination blob properties.
        :rtype: ~azure.storage.blob.models.BlobProperties
        """
        return super(CopyStatusPoller, self).result(timeout=timeout)



class CopyBlob(PollingMethod):
    """An empty poller that returns the deserialized initial response.
    """
    def __init__(self, interval, **kwargs):
        self._client = None
        self._status = None
        self._exception = None
        self.id = None
        self.etag = None
        self.last_modified = None
        self.polling_interval = interval
        self.kwargs = kwargs
        self.blob = None

    def _update_status(self):
        try:
            self.blob = self._client._client.blob.get_properties(  # pylint: disable=protected-access
                cls=deserialize_blob_properties, **self.kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self._status = self.blob.copy.status
        self.etag = self.blob.etag
        self.last_modified = self.blob.last_modified

    def initialize(self, client, initial_status, _):  # pylint: disable=arguments-differ
        # type: (Any, Any, Callable) -> None
        self._client = client
        if isinstance(initial_status, str):
            self.id = initial_status
            self._update_status()
        else:
            self._status = initial_status['copy_status']
            self.id = initial_status['copy_id']
            self.etag = initial_status['etag']
            self.last_modified = initial_status['last_modified']

    def run(self):
        # type: () -> None
        """Empty run, no polling."""

    def abort(self):
        # type: () -> None
        try:
            return self._client._client.blob.abort_copy_from_url(  # pylint: disable=protected-access
                self.id, **self.kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def status(self):
        # type: () -> str
        self._update_status()
        return self._status

    def finished(self):
        # type: () -> bool
        """Is this polling finished?
        :rtype: bool
        """
        return str(self.status()).lower() in ['success', 'aborted', 'failed']

    def resource(self):
        # type: () -> Any
        self._update_status()
        return self.blob


class CopyBlobPolling(CopyBlob):

    def run(self):
        # type: () -> None
        try:
            while not self.finished():
                self._update_status()
                time.sleep(self.polling_interval)
            if str(self.status()).lower() == 'aborted':
                raise ValueError("Copy operation aborted.")
            if str(self.status()).lower() == 'failed':
                raise ValueError("Copy operation failed: {}".format(self.blob.copy.status_description))
        except Exception as e:
            logger.warning(str(e))
            raise

    def status(self):
        # type: () -> str
        """Return the current status as a string.
        :rtype: str
        """
        try:
            return self._status.value # type: ignore
        except AttributeError:
            return self._status # type: ignore

    def resource(self):
        # type: () -> Any
        if not self.blob:
            self._update_status()
        return self.blob

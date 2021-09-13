# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from attr.setters import NO_OP


class ContentStreamDownloader():
    """A streaming object to download recording content.
    :ivar str endpoint:
        The url where the content is located.
    :ivar ~azure.communication.callingserver.ContentProperties properties:
        The properties of the content being downloaded. If only a range of the data is being
        downloaded, this will be reflected in the properties.
    :ivar int size:
        The size of the total data in the stream. This will be the byte range if speficied,
        otherwise the total size of the requested content.
    """
    def __init__(
        self,
        clients=None,
        config=None,
        start_range=None,
        end_range=None,
        max_concurrency=1,
        endpoint=None,
        **kwargs
    ):
        self.endpoint = endpoint
        self.properties = None
        self.size = None

        self._clients = clients
        self._config = config
        self._start_range = start_range
        self._end_range = end_range
        self._max_concurrency = max_concurrency
        self._request_options = kwargs
        self._download_complete = False
        self._current_content = None
        self._file_size = None
        self._non_empty_ranges = None
        self._response = None

    def _setup(self):
        NO_OP

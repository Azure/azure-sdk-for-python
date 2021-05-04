# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Iterator

from ._deserialize import from_blob_properties


class StorageStreamDownloader(object):
    """A streaming object to download from Azure Storage.

    :ivar str name:
        The name of the file being downloaded.
    :ivar ~azure.storage.filedatalake.FileProperties properties:
        The properties of the file being downloaded. If only a range of the data is being
        downloaded, this will be reflected in the properties.
    :ivar int size:
        The size of the total data in the stream. This will be the byte range if speficied,
        otherwise the total size of the file.
    """

    def __init__(self, downloader):
        self._downloader = downloader
        self.name = self._downloader.name
        self.properties = from_blob_properties(self._downloader.properties)  # pylint: disable=protected-access
        self.size = self._downloader.size

    def __len__(self):
        return self.size

    def chunks(self):
        # type: () -> Iterator[bytes]
        """Iterate over chunks in the download stream.

        :rtype: Iterator[bytes]
        """
        return self._downloader.chunks()

    def readall(self):
        """Download the contents of this file.

        This operation is blocking until all data is downloaded.
        :rtype: bytes or str
        """
        return self._downloader.readall()

    def readinto(self, stream):
        """Download the contents of this file to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The number of bytes read.
        :rtype: int
        """
        return self._downloader.readinto(stream)

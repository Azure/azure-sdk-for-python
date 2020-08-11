# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union, Iterable, IO  # pylint: disable=unused-import


class DataLakeFileQueryReader(object):  # pylint: disable=too-many-instance-attributes
    """A streaming object to read query results.

    :ivar str name:
        The name of the blob being quered.
    :ivar str container:
        The name of the container where the blob is.
    :ivar dict response_headers:
        The response_headers of the quick query request.
    :ivar bytes record_delimiter:
        The delimiter used to separate lines, or records with the data. The `records`
        method will return these lines via a generator.
    """

    def __init__(
        self,
        blob_query_reader
    ):
        self.name = blob_query_reader.name
        self.file_system = blob_query_reader.container
        self.response_headers = blob_query_reader.response_headers
        self.record_delimiter = blob_query_reader.record_delimiter
        self._bytes_processed = 0
        self._blob_query_reader = blob_query_reader

    def __len__(self):
        return len(self._blob_query_reader)

    def readall(self):
        # type: () -> Union[bytes, str]
        """Return all query results.

        This operation is blocking until all data is downloaded.
        If encoding has been configured - this will be used to decode individual
        records are they are received.

        :rtype: Union[bytes, str]
        """
        return self._blob_query_reader.readall()

    def readinto(self, stream):
        # type: (IO) -> None
        """Download the query result to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream.
        :returns: None
        """
        self._blob_query_reader(stream)

    def records(self):
        # type: () -> Iterable[Union[bytes, str]]
        """Returns a record generator for the query result.

        Records will be returned line by line.
        If encoding has been configured - this will be used to decode individual
        records are they are received.

        :rtype: Iterable[Union[bytes, str]]
        """
        return self._blob_query_reader.records()

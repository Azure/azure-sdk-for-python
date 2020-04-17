# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

from avro.datafile import DataFileReader
from avro.io import DatumReader

from ._models import QuickQueryError


class QuickQueryReader(object):  # pylint: disable=too-many-instance-attributes
    """A streaming object to read quick query result.

    :ivar str name:
        The name of the blob for the quick query request.
    :ivar str container:
        The name of the container where the blob is.
    :ivar dict response_headers:
        The response_headers of the quick query request.
    :ivar int total_bytes:
        The size of the total data in the stream.
    """

    def __init__(
        self,
        client=None,
        name=None,
        container=None,
        progress_callback=None,
        encoding=None,
        **kwargs
    ):
        self.name = name
        self.container = container
        self.response_headers = None
        self.total_bytes = None
        self.bytes_processed = 0
        self._progress_callback = progress_callback
        self._client = client
        self._request_options = kwargs
        self._encoding = encoding

    def __len__(self):
        return self.size

    def readall(self):
        """Return all quick query results.

        This operation is blocking until all data is downloaded.
        :rtype: bytes
        """
        stream = BytesIO()
        self.readinto(stream)
        data = stream.getvalue()
        if self._encoding:
            return data.decode(self._encoding)
        return data

    def readinto(self, stream):
        """Download the quick query result to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream.
        :returns: None
        """
        headers, raw_response_body = self._client.blob.quick_query(**self._request_options)
        self.response_headers = headers
        self._parse_quick_query_result(raw_response_body, stream, progress_callback=self._progress_callback)

    def _parse_quick_query_result(self, raw_response_body, stream, progress_callback=None):
        parsed_results = DataFileReader(QuickQueryStreamer(raw_response_body), DatumReader())
        for parsed_result in parsed_results:
            if parsed_result.get('data'):
                stream.write(parsed_result.get('data'))
                continue

            self.bytes_processed = parsed_result.get('bytesScanned')
            self.total_bytes = parsed_result.get('totalBytes')
            fatal = QuickQueryError(parsed_result['name'],
                                    parsed_result['fatal'],
                                    parsed_result['description'],
                                    parsed_result['position']) if parsed_result.get('fatal') else None
            if progress_callback:
                progress_callback(fatal, self.bytes_processed, self.total_bytes)


class QuickQueryStreamer(object):
    """
    File-like streaming iterator.
    """

    def __init__(self, generator):
        self.generator = generator
        self.iterator = iter(generator)
        self._buf = b""
        self._point = 0
        self.leftover = b""
        self.file_length = None

    def __len__(self):
        return self.file_length

    def __iter__(self):
        return self.iterator

    def seekable(self):
        return True

    def next(self):
        next_part = next(self.iterator)
        return next_part

    def tell(self):
        return self._point

    def seek(self, offset, whence=0):
        if whence == 0:
            self._point = offset
        elif whence == 1:
            self._point += offset
        else:
            raise ValueError("whence must be 0, or 1")
        if self._point < 0:
            self._point = 0  # XXX is this right?

    def read(self, size):
        try:
            # keep reading from the generator until the buffer of this stream has enough data to read
            while self._point + size > len(self._buf):
                self._buf += self.next()

            # if it's already EOF, get file_length right now
            self._buf += self.next()
        except StopIteration:
            self.file_length = len(self._buf)
            pass
        start_point = self._point

        # EOF
        if self._point + size > len(self._buf):
            self._point = len(self._buf)
        else:
            self._point += size

        return self._buf[start_point:self._point]

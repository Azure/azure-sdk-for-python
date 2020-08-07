# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines
import collections
import json
from datetime import datetime

from azure.storage.blob._shared.avro.datafile import DataFileReader
from azure.storage.blob._shared.avro.avro_io import DatumReader

from azure.core.exceptions import HttpResponseError
from azure.core.paging import PageIterator

# ===============================================================================================
SEGMENT_COMMON_PATH = "idx/segments/"
PATH_DELIMITER = "/"
# ===============================================================================================


class ChangeFeedPaged(PageIterator):
    """An Iterable of change feed events

    :ivar int results_per_page:
        The maximum number of results retrieved per API call.
    :ivar dict continuation_token:
        The continuation token to retrieve the next page of results.
    :ivar current_page:
        The current page of listed results.
    :vartype current_page: list(dict)

    :param ~azure.storage.blob.ContainerClient or ~azure.storage.blob.aio.ContainerClient:
        the client to get change feed events.
    :param int results_per_page:
        The maximum number of blobs to retrieve per
        call.
    :param datetime start_time:
        Filters the results to return only events which happened after this time.
    :param datetime end_time:
        Filters the results to return only events which happened before this time.
    :param dict continuation_token:
        An continuation token with which to start listing events from the previous position.
    """
    def __init__(
            self, container_client,
            results_per_page=None,
            start_time=None,
            end_time=None,
            continuation_token=None):
        if start_time and continuation_token:
            raise ValueError("start_time and continuation_token shouldn't be specified at the same time")
        super(ChangeFeedPaged, self).__init__(
            get_next=self._get_next_cf,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self.results_per_page = results_per_page or 5000
        self.current_page = None
        self._change_feed = ChangeFeed(container_client, self.results_per_page, start_time=start_time,
                                       end_time=end_time, cf_cursor=continuation_token)

    def _get_next_cf(self, continuation_token):  # pylint:disable=unused-argument
        try:
            return next(self._change_feed)
        except HttpResponseError:
            # TODO: we need to wrap the error
            pass

    def _extract_data_cb(self, event_list):
        self.current_page = event_list

        if self._change_feed.cursor:
            return self._change_feed.cursor, self.current_page
        return None, self.current_page


class ChangeFeed(object):
    def __init__(self, client, page_size, start_time=None, end_time=None, cf_cursor=None):
        self.client = client
        self.page_size = page_size
        self._segment_paths_generator = None
        self.current_segment = None
        self.start_time = start_time
        self.end_time = end_time
        self._initialize(cf_cursor=cf_cursor)
        self.cursor = None

    def __iter__(self):
        return self

    def __next__(self):
        change_feed = []
        remaining_to_load = self.page_size

        if not self.current_segment:
            raise StopIteration

        # reset the current segment page size. The page size which was set to remaining_to_load in the last call
        # could be very small
        self.current_segment.page_size = self.page_size

        while len(change_feed) < self.page_size and self.current_segment:
            try:
                page_of_events = next(self.current_segment)
                # extend the current page of events
                change_feed.extend(page_of_events)
                remaining_to_load -= len(page_of_events)
                self.cursor = {"segment_path": self.current_segment.segment_path,
                               "segment_cursor": self.current_segment.cursor}
            except StopIteration:
                self.cursor = None
                self.current_segment = self._get_next_segment(next(self._segment_paths_generator), remaining_to_load)

        if not change_feed:
            raise StopIteration
        return change_feed

    next = __next__  # Python 2 compatibility.

    def _initialize(self, cf_cursor=None):
        try:
            start_year = self.start_time.year
        except AttributeError:
            try:
                start_date = self._parse_datetime_from_segment_path(cf_cursor.get('segment_path'))
                start_year = start_date.year
            except AttributeError:
                start_year = ""

        # segment path generator will generate path starting from a specific year
        self._segment_paths_generator = self._get_segment_paths(start_year=start_year)
        next_segment_path = next(self._segment_paths_generator)

        # if start_time is specified, skip all segments earlier than start_time
        if self.start_time:
            while next_segment_path and self._is_earlier_than_start_time(next_segment_path):
                next_segment_path = next(self._segment_paths_generator)

        # if change_feed_cursor is specified, start from the specified segment
        if cf_cursor:
            while next_segment_path and next_segment_path != cf_cursor['segment_path']:
                next_segment_path = next(self._segment_paths_generator)

        self.current_segment = self._get_next_segment(
            next_segment_path,
            self.page_size,
            segment_cursor=cf_cursor['segment_cursor'] if cf_cursor else None)

    def _get_next_segment(self, segment_path, page_size, segment_cursor=None):
        if segment_path:
            if self.end_time and self._is_later_than_end_time(segment_path):
                return None
            return Segment(self.client, segment_path, page_size, segment_cursor)
        return None

    def _get_segment_paths(self, start_year=""):
        cur_year = datetime.today().year
        while not start_year or start_year <= cur_year:
            paths = self.client.list_blobs(name_starts_with=SEGMENT_COMMON_PATH + str(start_year))
            for path in paths:
                yield path.name

            # if not searching by prefix, all paths would have been iterated already, so it's time to yield None
            if not start_year:
                break
            # search the segment prefixed with next year.
            start_year += 1
        yield None

    @staticmethod
    def _parse_datetime_from_segment_path(segment_path):
        path_tokens = segment_path.split("/")
        year = int(path_tokens[2])
        month = int(path_tokens[3])
        day = int(path_tokens[4])
        hour = int(path_tokens[5][:2])
        return datetime(year, month, day, hour)

    def _is_earlier_than_start_time(self, segment_path):
        segment_date = self._parse_datetime_from_segment_path(segment_path)
        opaque_start_date = datetime(self.start_time.year, self.start_time.month,
                                     self.start_time.day, self.start_time.hour)

        return segment_date < opaque_start_date

    def _is_later_than_end_time(self, segment_path):
        segment_date = self._parse_datetime_from_segment_path(segment_path)
        opaque_end_date = datetime(self.end_time.year, self.end_time.month,
                                   self.end_time.day, self.end_time.hour)
        return segment_date > opaque_end_date


class Segment(object):
    def __init__(self, client, segment_path, page_size, segment_cursor=None):
        self.client = client
        self.segment_path = segment_path
        self.page_size = page_size
        self.shards = collections.deque()
        self._initialize(segment_cursor=segment_cursor)
        # cursor is in this format {"segment_path", path, "cur_shard": shard_path, "segment_cursor": shard_cursors_dict}
        self.cursor = {'shard_cursors': {}}

    def __iter__(self):
        return self

    def __next__(self):
        segment_events = []
        while len(segment_events) < self.page_size and self.shards:
            shard = self.shards.popleft()
            try:
                event = next(shard)
                segment_events.append(event)
                self.shards.append(shard)
                self.cursor['shard_cursors'][shard.shard_path] = shard.cursor
                self.cursor['cur_shard'] = shard.shard_path
            except StopIteration:
                self.cursor['shard_cursors'][shard.shard_path] = "EOF"

        if not segment_events:
            raise StopIteration

        return segment_events

    next = __next__  # Python 2 compatibility.

    def _initialize(self, segment_cursor=None):
        segment_content = self.client.get_blob_client(self.segment_path).download_blob().readall()
        segment_content = segment_content.decode()
        segment_dict = json.loads(segment_content)

        # Don't read unfinalized segment, else the items events will change for every time reading
        if segment_dict['status'] != 'Finalized':
            return

        raw_shard_paths = segment_dict['chunkFilePaths']
        shard_paths = []
        # to strip the overhead of all raw shard paths
        for raw_shard_path in raw_shard_paths:
            shard_paths.append(raw_shard_path.replace('$blobchangefeed/', '', 1))

        # TODO: we can optimize to initiate shards in parallel
        if not segment_cursor:
            for shard_path in shard_paths:
                self.shards.append(Shard(self.client, shard_path))
        else:
            start_shard_path = segment_cursor['cur_shard']

            if shard_paths:
                # Initialize all shards using the shard cursors, skip those finished shards
                for shard_path in shard_paths:
                    if segment_cursor['shard_cursors'].get(shard_path) != "EOF":
                        self.shards.append(Shard(self.client, shard_path,
                                                 segment_cursor['shard_cursors'].get(shard_path)))
                    else:
                        # if the shards has reached EOF, track it in cursor
                        self.cursor['shard_cursors'][shard_path] = "EOF"

                # the move the shard behind start_shard_path one to the left most place, the left most shard is the next
                # shard we should read based on continuation token.
                while self.shards[0].shard_path != start_shard_path:
                    self.shards.append(self.shards.popleft())
                self.shards.append(self.shards.popleft())


class Shard(object):
    def __init__(self, client, shard_path, shard_cursor=None):
        self.client = client
        self.shard_path = shard_path
        self.current_chunk = None
        self.unprocessed_chunk_path_props = []
        self._initialize(shard_cursor=shard_cursor)
        self.cursor = None  # to track the chunk info we are reading

    def __iter__(self):
        return self

    def __next__(self):
        next_event = None
        while not next_event and self.current_chunk:
            try:
                next_event = next(self.current_chunk)
                self.cursor = {'chunk_path': self.current_chunk.chunk_path, 'chunk_cursor': self.current_chunk.cursor}
            except StopIteration:
                self.cursor = None
                self.current_chunk = self._get_next_chunk()

        if not next_event:
            raise StopIteration

        return next_event

    next = __next__  # Python 2 compatibility.

    def _initialize(self, shard_cursor=None):
        # To get all chunk file paths
        self.unprocessed_chunk_path_props = collections.deque(self.client.list_blobs(name_starts_with=self.shard_path))

        # move cursor to the expected chunk
        if shard_cursor:
            while self.unprocessed_chunk_path_props and \
                    self.unprocessed_chunk_path_props[0].name != shard_cursor.get('chunk_path'):
                self.unprocessed_chunk_path_props.popleft()
            self.current_chunk = self._get_next_chunk(chunk_cursor=shard_cursor.get('chunk_cursor'))
        else:
            self.current_chunk = self._get_next_chunk()

    def _get_next_chunk(self, chunk_cursor=None):
        if self.unprocessed_chunk_path_props:
            current_chunk_path = self.unprocessed_chunk_path_props.popleft()
            return Chunk(self.client, current_chunk_path.name, chunk_cursor=chunk_cursor)
        return None


class Chunk(object):
    def __init__(self, client, chunk_path, chunk_cursor=None):
        self.client = client
        self.chunk_path = chunk_path
        self.file_reader = None
        self.cursor = None  # to track the current position in avro file
        self._data_stream = None
        self._initialize(chunk_cursor=chunk_cursor)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            event = next(self.file_reader)
            self.cursor = {'id': event['id'],
                           'position': self._data_stream.event_position,
                           'block_count': self._data_stream.block_count
                           }
            return event
        except StopIteration:
            self.cursor = None
            raise StopIteration

    next = __next__  # Python 2 compatibility.

    def _initialize(self, chunk_cursor=None):
        # To get all events in a chunk
        blob_client = self.client.get_blob_client(self.chunk_path)

        file_offset = chunk_cursor.get('position') if chunk_cursor else 0
        block_count = chunk_cursor.get('block_count') if chunk_cursor else 0

        # An offset means the avro data doesn't have avro header,
        # so only when the data stream has a offset we need header stream to help
        header_stream = ChangeFeedStreamer(blob_client) if file_offset else None
        self._data_stream = ChangeFeedStreamer(blob_client, chunk_file_start=file_offset, block_count=block_count)
        self.file_reader = DataFileReader(self._data_stream, DatumReader(), header_reader=header_stream)

        # After initializing DataFileReader, data_stream cursor has been moved to the data part(DataFileReader read
        # the header part during initialization)
        self._data_stream.event_position = self._data_stream.tell()


class ChangeFeedStreamer(object):
    """
    File-like streaming iterator.
    """

    def __init__(self, blob_client, chunk_file_start=0, block_count=0):
        self._chunk_file_start = chunk_file_start or 0  # this value will never be updated
        self._download_offset = self._chunk_file_start  # range start of the next download
        self.event_position = self._chunk_file_start  # track the most recently read sync marker position
        self.block_count = block_count
        self._point = self._chunk_file_start  # file cursor position relative to the whole chunk file, not the buffered
        self._chunk_size = 4 * 1024 * 1024
        self._buf = b''
        self._buf_start = self._chunk_file_start  # the start position of the chunk file to buffer
        self._iterator = blob_client.download_blob(offset=self._chunk_file_start).chunks()

    def __len__(self):
        return self._download_offset

    def __iter__(self):
        return self._iterator

    @staticmethod
    def seekable():
        return True

    def __next__(self):
        next_chunk = next(self._iterator)
        self._download_offset += len(next_chunk)
        return next_chunk

    next = __next__  # Python 2 compatibility.

    def tell(self):
        return self._point

    def seek(self, offset, whence=0):
        if whence == 0:
            self._point = self._chunk_file_start + offset
        elif whence == 1:
            self._point += offset
        else:
            raise ValueError("whence must be 0, or 1")
        if self._point < self._chunk_file_start:
            self._point = self._chunk_file_start

    def read(self, size):
        try:
            # keep downloading file content until the buffer has enough bytes to read
            while self._point + size > self._download_offset:
                next_data_chunk = self.__next__()
                self._buf += next_data_chunk
        except StopIteration:
            pass

        start_point = self._point

        # EOF
        self._point = min(self._point + size, self._download_offset)

        # seek the cursor's relative position in the buffer
        relative_start = start_point - self._buf_start
        if relative_start < 0:
            raise ValueError("Buffer has dumped too much data")
        relative_end = relative_start + size
        data = self._buf[relative_start: relative_end]

        # dump the extra data in buffer
        # buffer start--------------------16bytes----current read position
        dumped_size = max(relative_end - 16 - relative_start, 0)
        self._buf_start += dumped_size
        self._buf = self._buf[dumped_size:]

        return data

    def track_event_position(self):
        self.event_position = self.tell()

# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import sys
try:
    from collections.abc import Iterator
    xrange = range
except ImportError:
    from collections import Iterator

from typing import Dict, Any, List, Callable, Optional, TYPE_CHECKING  # pylint: disable=unused-import

from msrest.serialization import Deserializer

if TYPE_CHECKING:
    from .pipeline.transport import HttpResponse  # pylint: disable=unused-import
    from msrest.serialization import Model  # pylint: disable=unused-import

if sys.version_info >= (3, 5, 2):
    # Not executed on old Python, no syntax error
    from .async_paging import AsyncPagedMixin  # type: ignore
else:
    class AsyncPagedMixin(object):  # type: ignore
        pass

class Paged(AsyncPagedMixin, Iterator):
    """A container for paged REST responses.

    :param HttpResponse response: server response object.
    :param callable command: Function to retrieve the next page of items.
    :param dict classes: A dictionary of class dependencies for
     deserialization.
    :param dict raw_headers: A dict of raw headers to add if "raw" is called
    """
    _validation = {}  # type: Dict[str, Dict[str, Any]]
    _attribute_map = {}  # type: Dict[str, Dict[str, Any]]

    def __init__(self, command, classes, raw_headers=None, **kwargs):
        # type: (Callable[[str], HttpResponse], Dict[str, Model], Dict[str, str], Any) -> None
        super(Paged, self).__init__(**kwargs)  # type: ignore
        # Sets next_link, current_page, and _current_page_iter_index.
        self.next_link = ""
        self.current_page = []  # type: List[Model]
        self._current_page_iter_index = 0
        self._deserializer = Deserializer(classes)
        self._get_next = command
        self._response = None  # type: Optional[HttpResponse]
        self._raw_headers = raw_headers

    def __iter__(self):
        """Return 'self'."""
        # Since iteration mutates this object, consider it an iterator in-and-of
        # itself.
        return self

    @classmethod
    def _get_subtype_map(cls):
        """Required for parity to Model object for deserialization."""
        return {}

    def _advance_page(self):
        # type: () -> List[Model]
        """Force moving the cursor to the next azure call.

        This method is for advanced usage, iterator protocol is prefered.

        :raises: StopIteration if no further page
        :return: The current page list
        :rtype: list
        """
        if self.next_link is None:
            raise StopIteration("End of paging")
        self._current_page_iter_index = 0
        self._response = self._get_next(self.next_link)
        self._deserializer(self, self._response)
        return self.current_page

    def __next__(self):
        """Iterate through responses."""
        # Storing the list iterator might work out better, but there's no
        # guarantee that some code won't replace the list entirely with a copy,
        # invalidating an list iterator that might be saved between iterations.
        if self.current_page and self._current_page_iter_index < len(self.current_page):
            response = self.current_page[self._current_page_iter_index]
            self._current_page_iter_index += 1
            return response
        else:
            self._advance_page()
            return self.__next__()

    next = __next__  # Python 2 compatibility.

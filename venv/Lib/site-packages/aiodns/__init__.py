
import asyncio
import functools
import pycares

from typing import (
    Any,
    List,
    Optional,
)

# TODO: Work out mypy no attribute error and remove ignore
from . import error # type: ignore


__version__ = '2.0.0'

__all__ = ('DNSResolver', 'error')


READ = 1
WRITE = 2

query_type_map = {'A'     : pycares.QUERY_TYPE_A,
                  'AAAA'  : pycares.QUERY_TYPE_AAAA,
                  'ANY'   : pycares.QUERY_TYPE_ANY,
                  'CNAME' : pycares.QUERY_TYPE_CNAME,
                  'MX'    : pycares.QUERY_TYPE_MX,
                  'NAPTR' : pycares.QUERY_TYPE_NAPTR,
                  'NS'    : pycares.QUERY_TYPE_NS,
                  'PTR'   : pycares.QUERY_TYPE_PTR,
                  'SOA'   : pycares.QUERY_TYPE_SOA,
                  'SRV'   : pycares.QUERY_TYPE_SRV,
                  'TXT'   : pycares.QUERY_TYPE_TXT
        }


class DNSResolver:
    def __init__(self, nameservers=None, loop=None, **kwargs):
        # type: (Optional[List[str]], Optional[asyncio.AbstractEventLoop], Any) -> None
        self.loop = loop or asyncio.get_event_loop()
        assert self.loop is not None
        kwargs.pop('sock_state_cb', None)
        self._channel = pycares.Channel(sock_state_cb=self._sock_state_cb, **kwargs)
        if nameservers:
            self.nameservers = nameservers
        self._read_fds = set() # type: Set[int]
        self._write_fds = set() # type: Set[int]
        self._timer = None

    @property
    def nameservers(self):
        # type: () -> pycares.Channel
        return self._channel.servers

    @nameservers.setter
    def nameservers(self, value):
        # type: (List[str]) -> None
        self._channel.servers = value

    @staticmethod
    def _callback(fut, result, errorno):
        # type: (asyncio.Future, Any, int) -> None
        if fut.cancelled():
            return
        if errorno is not None:
            fut.set_exception(error.DNSError(errorno, pycares.errno.strerror(errorno)))
        else:
            fut.set_result(result)

    def query(self, host, qtype):
        # type: (str, str) -> asyncio.Future
        try:
            qtype = query_type_map[qtype]
        except KeyError:
            raise ValueError('invalid query type: {}'.format(qtype))
        fut = asyncio.Future(loop=self.loop)
        cb = functools.partial(self._callback, fut)
        self._channel.query(host, qtype, cb)
        return fut

    def gethostbyname(self, host, family):
        # type: (str, str) -> asyncio.Future
        fut = asyncio.Future(loop=self.loop)
        cb = functools.partial(self._callback, fut)
        self._channel.gethostbyname(host, family, cb)
        return fut

    def gethostbyaddr(self, name):
        # type: (str) -> asyncio.Future
        fut = asyncio.Future(loop=self.loop)
        cb = functools.partial(self._callback, fut)
        self._channel.gethostbyaddr(name, cb)
        return fut

    def cancel(self):
        # type: () -> None
        self._channel.cancel()

    def _sock_state_cb(self, fd, readable, writable):
        # type: (int, bool, bool) -> None
        if readable or writable:
            if readable:
                self.loop.add_reader(fd, self._handle_event, fd, READ)
                self._read_fds.add(fd)
            if writable:
                self.loop.add_writer(fd, self._handle_event, fd, WRITE)
                self._write_fds.add(fd)
            if self._timer is None:
                self._timer = self.loop.call_later(1.0, self._timer_cb)
        else:
            # socket is now closed
            if fd in self._read_fds:
                self._read_fds.discard(fd)
                self.loop.remove_reader(fd)

            if fd in self._write_fds:
                self._write_fds.discard(fd)
                self.loop.remove_writer(fd)

            if not self._read_fds and not self._write_fds and self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def _handle_event(self, fd, event):
        # type: (int, Any) -> None
        read_fd = pycares.ARES_SOCKET_BAD
        write_fd = pycares.ARES_SOCKET_BAD
        if event == READ:
            read_fd = fd
        elif event == WRITE:
            write_fd = fd
        self._channel.process_fd(read_fd, write_fd)

    def _timer_cb(self):
        # type: () -> None
        if self._read_fds or self._write_fds:
            self._channel.process_fd(pycares.ARES_SOCKET_BAD, pycares.ARES_SOCKET_BAD)
            self._timer = self.loop.call_later(1.0, self._timer_cb)
        else:
            self._timer = None


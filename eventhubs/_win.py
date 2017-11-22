# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Provides Windows specific implementations.
"""

# pylint: disable=line-too-long
# pylint: disable=C0111
# pylint: disable=W0613
# pylint: disable=W0702

import logging
import socket
import errno
from proton import generate_uuid

try:
    import Queue
except:
    import queue as Queue

class Pipe(object):
    def __init__(self):
        self.source = None
        self.sink = None

    @classmethod
    def open(cls, owner=None):
        port = -1
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(25672, 35672):
            port = i
            try:
                listener.bind(("127.0.0.1", port))
                break
            except socket.error as err:
                if err.errno != errno.EADDRINUSE:
                    logging.error("%s: pipe socket bind failed %s", owner, err)
                    raise
        listener.listen(1)
        client = None
        server = None
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setblocking(False)
            client.connect_ex(("127.0.0.1", port))
            server, address = listener.accept()
            logging.info("%s: pipe accepted socket from %s", owner, address)
            client.setblocking(True)
            code = generate_uuid().bytes
            client.sendall(code)
            code2 = Pipe._recvall(server, len(code))
            if code != code2:
                raise IOError(errno.EIO, "Pipe handshake failed")

            pipe = Pipe()
            pipe.sink = client
            pipe.source = server
            return pipe
        except:
            if client:
                client.close()
            if server:
                server.close()
            raise
        finally:
            listener.close()

    def close(self):
        if self.sink:
            self.sink.close()
        if self.source:
            self.source.close()

    @classmethod
    def _recvall(cls, source, count):
        data = b''
        while count > 0:
            packet = source.recv(64)
            if not packet:
                return None
            data += packet
            count -= len(packet)
        return data

class EventInjector(object):
    """
    The injector provided by proton does not work on Windows because
    anonymous pipe cannot be used in select. Implement a workaround
    using a pair of sockets.
    https://issues.apache.org/jira/browse/PROTON-1071
    """
    def __init__(self):
        self.queue = Queue.Queue()
        self.pipe = Pipe.open()
        self._closed = False

    def trigger(self, event):
        self.queue.put(event)
        self.pipe.sink.send(b'!')

    def close(self):
        self._closed = True
        self.pipe.sink.send(b'!')

    def on_selectable_init(self, event):
        sel = event.context
        sel.fileno(self.pipe.source.fileno())
        sel.reading = True
        event.reactor.update(sel)

    def on_selectable_readable(self, event):
        self.pipe.source.recv(256)
        while not self.queue.empty():
            requested = self.queue.get()
            event.reactor.push_event(requested.context, requested.type)
        if self._closed:
            sel = event.context
            sel.terminate()
            event.reactor.update(sel)
        else:
            # hack to start iocp reading for external
            # sockets
            event.reactor.update(event.context)

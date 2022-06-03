# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import itertools
from threading import Timer, Lock

# Credit to https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            # NOTE: If there is a concern about perf impact of this Timer, we'd need to convert to multiprocess and use IPC.

            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


# Credit to https://julien.danjou.info/atomic-lock-free-counters-in-python/
class AtomicCounter(object):

    def __init__(self):
        self._number_of_read = 0
        self._counter = itertools.count()
        self._read_lock = Lock()

    def increment(self):
        next(self._counter)
    
    def reset(self):
        with self._read_lock:
            self._number_of_read = 0
            self._counter = itertools.count()

    def value(self):
        with self._read_lock:
            value = next(self._counter) - self._number_of_read
            self._number_of_read += 1
        return value

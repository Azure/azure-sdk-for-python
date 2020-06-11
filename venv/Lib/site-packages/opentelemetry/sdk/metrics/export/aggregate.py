# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
import threading
from collections import namedtuple


class Aggregator(abc.ABC):
    """Base class for aggregators.

    Aggregators are responsible for holding aggregated values and taking a
    snapshot of these values upon export (checkpoint).
    """

    def __init__(self):
        self.current = None
        self.checkpoint = None

    @abc.abstractmethod
    def update(self, value):
        """Updates the current with the new value."""

    @abc.abstractmethod
    def take_checkpoint(self):
        """Stores a snapshot of the current value."""

    @abc.abstractmethod
    def merge(self, other):
        """Combines two aggregator values."""


class CounterAggregator(Aggregator):
    """Aggregator for Counter metrics."""

    def __init__(self):
        super().__init__()
        self.current = 0
        self.checkpoint = 0
        self._lock = threading.Lock()

    def update(self, value):
        with self._lock:
            self.current += value

    def take_checkpoint(self):
        with self._lock:
            self.checkpoint = self.current
            self.current = 0

    def merge(self, other):
        with self._lock:
            self.checkpoint += other.checkpoint


class MinMaxSumCountAggregator(Aggregator):
    """Agregator for Measure metrics that keeps min, max, sum and count."""

    _TYPE = namedtuple("minmaxsumcount", "min max sum count")
    _EMPTY = _TYPE(None, None, None, 0)

    @classmethod
    def _merge_checkpoint(cls, val1, val2):
        if val1 is cls._EMPTY:
            return val2
        if val2 is cls._EMPTY:
            return val1
        return cls._TYPE(
            min(val1.min, val2.min),
            max(val1.max, val2.max),
            val1.sum + val2.sum,
            val1.count + val2.count,
        )

    def __init__(self):
        super().__init__()
        self.current = self._EMPTY
        self.checkpoint = self._EMPTY
        self._lock = threading.Lock()

    def update(self, value):
        with self._lock:
            if self.current is self._EMPTY:
                self.current = self._TYPE(value, value, value, 1)
            else:
                self.current = self._TYPE(
                    min(self.current.min, value),
                    max(self.current.max, value),
                    self.current.sum + value,
                    self.current.count + 1,
                )

    def take_checkpoint(self):
        with self._lock:
            self.checkpoint = self.current
            self.current = self._EMPTY

    def merge(self, other):
        with self._lock:
            self.checkpoint = self._merge_checkpoint(
                self.checkpoint, other.checkpoint
            )


class ObserverAggregator(Aggregator):
    """Same as MinMaxSumCount but also with last value."""

    _TYPE = namedtuple("minmaxsumcountlast", "min max sum count last")

    def __init__(self):
        super().__init__()
        self.mmsc = MinMaxSumCountAggregator()
        self.current = None
        self.checkpoint = self._TYPE(None, None, None, 0, None)

    def update(self, value):
        self.mmsc.update(value)
        self.current = value

    def take_checkpoint(self):
        self.mmsc.take_checkpoint()
        self.checkpoint = self._TYPE(*(self.mmsc.checkpoint + (self.current,)))

    def merge(self, other):
        self.mmsc.merge(other.mmsc)
        self.checkpoint = self._TYPE(
            *(
                self.mmsc.checkpoint
                + (other.checkpoint.last or self.checkpoint.last,)
            )
        )

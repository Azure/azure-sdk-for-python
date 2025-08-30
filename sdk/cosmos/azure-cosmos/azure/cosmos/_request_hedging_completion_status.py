# The MIT License (MIT)
# Copyright (c) 2018 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module for hedging completion status tracking."""
from abc import ABC, abstractmethod
from threading import Event


class HedgingCompletionStatus(ABC):
    """Abstract base class for tracking request hedging completion status.
    
    This class defines the interface for both synchronous and asynchronous
    implementations of completion status tracking.
    """

    @property
    @abstractmethod
    def is_completed(self) -> bool:
        """Check if request is completed.
        
        This is a non-blocking operation that returns immediately.
        
        :returns: True if request is completed, False otherwise
        :rtype: bool
        """

    @abstractmethod
    def set_completed(self) -> None:
        """Signal request completion.
        
        This is a non-blocking operation that sets completion status to True.
        Once set, is_completed will always return True.
        """


class SyncHedgingCompletionStatus(HedgingCompletionStatus):
    """Thread-safe implementation of completion status using Threading.Event."""

    def __init__(self):
        """Initialize completion status with a Threading.Event."""
        self._completed = Event()

    @property
    def is_completed(self) -> bool:
        """Check if request is completed (non-blocking).
        
        :returns: True if request is completed, False otherwise
        :rtype: bool
        """
        return self._completed.is_set()

    def set_completed(self) -> None:
        """Signal request completion (non-blocking)."""
        self._completed.set()

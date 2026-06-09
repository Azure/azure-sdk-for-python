# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

from typing import Any, Iterable, Mapping, Optional

from azure.core.async_paging import AsyncItemPaged
from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict

from ._diagnostics import (
    HEDGING_STATE_HEADER_KEY,
    _HedgingDetectionAccessorsMixin,
    _pop_state_from_headers,
)


class CosmosItemPaged(_HedgingDetectionAccessorsMixin, ItemPaged[dict[str, Any]]):
    """A custom ItemPaged class that provides access to response headers from query operations.

    This class wraps the standard ItemPaged and provides access to the most recent
    response headers captured during pagination via a shared dict populated by __QueryFeed.

    It also exposes three hedging-detection accessors inherited from
    :class:`~azure.cosmos._diagnostics._HedgingDetectionAccessorsMixin`:
    :meth:`is_hedging_started`, :meth:`get_requested_regions`, and
    :meth:`get_responded_regions`. The accessors reflect the hedging state of
    the **most recently fetched** page; pre-fetch they return safe defaults
    (``False`` / empty tuples).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        popped = kwargs.pop('response_headers', None)
        self._response_headers: CaseInsensitiveDict = popped if popped is not None else CaseInsensitiveDict()
        super().__init__(*args, **kwargs)
        # Latched hedging-detection state. The shared ``_response_headers`` dict
        # is populated lazily as pages are fetched; the orchestrator stashes the
        # per-operation state under a private sentinel key that we latch here so
        # the accessors keep working after the headers dict is cleared/reused.
        self._hedging_state_cached = None

    @property
    def _hedging_state(self):
        state = self._response_headers.get(HEDGING_STATE_HEADER_KEY) if self._response_headers else None
        if state is not None:
            self._hedging_state_cached = state
        return self._hedging_state_cached

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        copied = self._response_headers.copy()
        copied.pop(HEDGING_STATE_HEADER_KEY, None)
        return copied


class CosmosAsyncItemPaged(_HedgingDetectionAccessorsMixin, AsyncItemPaged[dict[str, Any]]):
    """A custom AsyncItemPaged class that provides access to response headers from async query operations.

    This class wraps the standard AsyncItemPaged and provides access to the most recent
    response headers captured during pagination via a shared dict populated by __QueryFeed.

    Also exposes the three hedging-detection accessors inherited from
    :class:`~azure.cosmos._diagnostics._HedgingDetectionAccessorsMixin`. The
    accessors reflect the hedging state of the **most recently fetched** page;
    pre-fetch they return safe defaults (``False`` / empty tuples).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        popped = kwargs.pop('response_headers', None)
        self._response_headers: CaseInsensitiveDict = popped if popped is not None else CaseInsensitiveDict()
        super().__init__(*args, **kwargs)
        self._hedging_state_cached = None

    @property
    def _hedging_state(self):
        state = self._response_headers.get(HEDGING_STATE_HEADER_KEY) if self._response_headers else None
        if state is not None:
            self._hedging_state_cached = state
        return self._hedging_state_cached

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers from the most recent page fetch.

        :return: Response headers from the last page, or empty dict if no pages have been fetched
        :rtype: ~azure.core.utils.CaseInsensitiveDict
        """
        copied = self._response_headers.copy()
        copied.pop(HEDGING_STATE_HEADER_KEY, None)
        return copied


class CosmosDict(_HedgingDetectionAccessorsMixin, dict[str, Any]):
    def __init__(self, original_dict: Optional[Mapping[str, Any]], /, *, response_headers: CaseInsensitiveDict) -> None:
        if original_dict is None:
            original_dict = {}
        super().__init__(original_dict)
        # Pull the hedging-detection state off the headers dict (if attached
        # by the orchestrator) before storing the headers, so customers never
        # see the private sentinel via ``get_response_headers()``.
        self._hedging_state = _pop_state_from_headers(response_headers)
        self._response_headers = response_headers

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers associated to this response

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers.copy()


class CosmosList(_HedgingDetectionAccessorsMixin, list[dict[str, Any]]):
    def __init__(self, original_list: Optional[Iterable[dict[str, Any]]], /, *,
                 response_headers: CaseInsensitiveDict) -> None:
        if original_list is None:
            original_list = []
        super().__init__(original_list)
        self._hedging_state = _pop_state_from_headers(response_headers)
        self._response_headers = response_headers

    def get_response_headers(self) -> CaseInsensitiveDict:
        """Returns a copy of the response headers associated to this response

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers.copy()

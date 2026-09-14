# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep customer callback failures outside page retry handling."""

from typing import Any, Callable, Mapping


class PageResponseHookError(Exception):
    """Carry a callback error through transport retries without classifying it as a service error."""

    def __init__(self, original: Exception) -> None:
        super().__init__(str(original))
        self.original = original


def wrap_page_response_hook(
    hook: Callable[[Mapping[str, Any]], None],
) -> Callable[[Mapping[str, Any], Any], None]:
    def on_response(headers: Mapping[str, Any], _body: Any) -> None:
        try:
            hook(dict(headers))
        except Exception as error:
            # The public pager restores the original exception after retry handling.
            raise PageResponseHookError(error) from error

    return on_response

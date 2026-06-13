# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Every point operation should offer the same ``response_hook`` callback,
spelled the same way on both the sync and async clients.

Why a dedicated test: the hook keeps working even when a method forgets to
list it, because it can quietly slip in through ``**kwargs``. So a passing
call doesn't prove the parameter is really part of the public surface.
These tests check the surface itself, so a method that drops the parameter
fails here instead of passing unnoticed -- which is exactly how three async
methods (read / upsert / replace) drifted once.

Pure introspection: no network, no emulator, no Rust binding.
"""
import inspect
import unittest
from typing import Any, Callable, Mapping, Optional

from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos.container import ContainerProxy as SyncContainerProxy


# The six single-item operations that route through the backend dispatch path.
_POINT_METHODS = [
    "create_item",
    "read_item",
    "upsert_item",
    "replace_item",
    "patch_item",
    "delete_item",
]

# The hook shape every body-returning point op shares: (headers, item) -> None.
_ITEM_HOOK = Optional[Callable[[Mapping[str, str], dict[str, Any]], None]]
# delete_item returns no body, so its second argument is None.
_DELETE_HOOK = Optional[Callable[[Mapping[str, str], None], None]]

_EXPECTED_HOOK = {
    "create_item": _ITEM_HOOK,
    "read_item": _ITEM_HOOK,
    "upsert_item": _ITEM_HOOK,
    "replace_item": _ITEM_HOOK,
    "patch_item": _ITEM_HOOK,
    "delete_item": _DELETE_HOOK,
}

_SURFACES = (("sync", SyncContainerProxy), ("async", AsyncContainerProxy))


def _response_hook_param(cls, method_name):
    """Return the ``response_hook`` Parameter for ``cls.method_name`` (or None)."""
    signature = inspect.signature(getattr(cls, method_name))
    return signature.parameters.get("response_hook")


def _normalise(annotation):
    """A whitespace-insensitive string form of an annotation, for comparison.

    Both the live annotation and the expected one are real typing objects,
    so ``str()`` renders them the same way (``typing.Any`` / ``NoneType``
    prefixes appear on both sides and cancel out).
    """
    return "".join(str(annotation).split())


class TestResponseHookIsExplicitOnEveryPointMethod(unittest.TestCase):
    """The hook is a real, visible parameter on every point operation."""

    def test_sync_and_async_declare_response_hook_explicitly(self):
        """Proves every point operation, on both clients, offers ``response_hook``
        as a first-class optional parameter callers can discover -- not a
        hidden extra that only happens to work."""
        for method_name in _POINT_METHODS:
            for label, cls in _SURFACES:
                with self.subTest(method=method_name, surface=label):
                    param = _response_hook_param(cls, method_name)
                    self.assertIsNotNone(
                        param,
                        "{} {} must declare 'response_hook' explicitly, not "
                        "only via **kwargs".format(label, method_name),
                    )
                    self.assertEqual(
                        param.kind,
                        inspect.Parameter.KEYWORD_ONLY,
                        "{} {}: 'response_hook' must be keyword-only".format(label, method_name),
                    )
                    self.assertIsNone(
                        param.default,
                        "{} {}: 'response_hook' must default to None".format(label, method_name),
                    )


class TestResponseHookTypeMatchesExpectedShape(unittest.TestCase):
    """The hook advertises the right shape, and advertises it the same way everywhere."""

    def test_annotation_matches_expected(self):
        """Proves each operation's hook promises the callback it actually calls:
        one given the response headers and the returned item."""
        for method_name in _POINT_METHODS:
            expected = _normalise(_EXPECTED_HOOK[method_name])
            for label, cls in _SURFACES:
                with self.subTest(method=method_name, surface=label):
                    param = _response_hook_param(cls, method_name)
                    self.assertIsNotNone(param, "{} {} missing response_hook".format(label, method_name))
                    self.assertEqual(
                        _normalise(param.annotation),
                        expected,
                        "{} {}: 'response_hook' annotation is not the expected "
                        "callback shape".format(label, method_name),
                    )

    def test_sync_and_async_annotations_are_identical(self):
        """Proves the sync and async clients describe the same operation's hook
        identically, so the two surfaces can't quietly drift apart."""
        for method_name in _POINT_METHODS:
            with self.subTest(method=method_name):
                sync_annotation = _normalise(_response_hook_param(SyncContainerProxy, method_name).annotation)
                async_annotation = _normalise(_response_hook_param(AsyncContainerProxy, method_name).annotation)
                self.assertEqual(
                    sync_annotation,
                    async_annotation,
                    "{}: sync and async 'response_hook' annotations differ".format(method_name),
                )

    def test_delete_item_hook_has_no_response_body(self):
        """Proves a delete's hook reflects that a delete returns nothing: its
        callback is handed no item, unlike every other operation."""
        for label, cls in _SURFACES:
            with self.subTest(surface=label):
                annotation = _normalise(_response_hook_param(cls, "delete_item").annotation)
                self.assertEqual(annotation, _normalise(_DELETE_HOOK))
                self.assertNotEqual(annotation, _normalise(_ITEM_HOOK))


if __name__ == "__main__":
    unittest.main()

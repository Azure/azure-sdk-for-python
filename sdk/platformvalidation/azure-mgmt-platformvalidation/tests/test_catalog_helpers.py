# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from types import SimpleNamespace

import pytest

from test_catalog import TestCatalog as CatalogTestCase


@pytest.mark.parametrize(
    "subscription_id",
    ["11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"],
)
@pytest.mark.parametrize(
    "resource",
    [
        "validationTests/boot",
        "validationTests/boot/versions/1.0.0",
        "validationTestCategories/image-certification",
    ],
)
def test_catalog_identity_is_subscription_scoped(monkeypatch, resource, subscription_id):
    case = CatalogTestCase()
    monkeypatch.setattr(case, "get_settings_value", lambda _: subscription_id)
    provider_id = f"/providers/Microsoft.PlatformValidation/{resource}"
    expected = f"/subscriptions/{subscription_id}{provider_id}"
    assert case.catalog_id(resource) == expected
    entry = SimpleNamespace(
        name=resource.rsplit("/", 1)[-1],
        id=expected,
        properties=SimpleNamespace(audience="Public"),
    )
    case.assert_entry(entry, expected, entry.name)
    for invalid_id in (provider_id, f"/subscriptions/unexpected{provider_id}"):
        entry.id = invalid_id
        with pytest.raises(AssertionError, match="subscription-scoped"):
            case.assert_entry(entry, expected, entry.name)

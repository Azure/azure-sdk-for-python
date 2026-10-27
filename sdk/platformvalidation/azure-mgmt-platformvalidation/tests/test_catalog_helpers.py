# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from types import SimpleNamespace

import pytest

from test_catalog import TestCatalog as CatalogTestCase


@pytest.mark.parametrize(
    "resource",
    [
        "validationTests/boot",
        "validationTests/boot/versions/1.0.0",
        "validationTestCategories/image-certification",
    ],
)
def test_catalog_identity_is_provider_global(resource):
    case = CatalogTestCase()
    expected = f"/providers/Microsoft.PlatformValidation/{resource}"
    assert case.catalog_id(resource) == expected
    entry = SimpleNamespace(
        name=resource.rsplit("/", 1)[-1],
        id=expected,
        properties=SimpleNamespace(audience="Public"),
    )
    case.assert_entry(entry, expected, entry.name)
    entry.id = f"/subscriptions/unexpected{expected}"
    with pytest.raises(AssertionError, match="provider-global"):
        case.assert_entry(entry, expected, entry.name)

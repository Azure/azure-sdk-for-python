# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests that verify the ``aio`` extras are declared on the package."""

import re
import unittest
from importlib import metadata as importlib_metadata

import pytest

from azure.cosmos.aio import CosmosClient  # noqa: F401


@pytest.mark.cosmosEmulator
class TestAioExtrasPackaging(unittest.TestCase):

    def test_aio_extras_declared_in_distribution_metadata(self):
        # The installed package must advertise the ``aio`` extra and
        # route it to azure-core with the ``aio`` extra at version 1.30
        # or newer, so ``pip install azure-cosmos[aio]`` pulls aiohttp.
        try:
            dist = importlib_metadata.distribution("azure-cosmos")
        except importlib_metadata.PackageNotFoundError:
            self.skipTest("azure-cosmos is not installed in this interpreter.")

        provides_extra = dist.metadata.get_all("Provides-Extra") or []
        self.assertIn("aio", provides_extra)

        requires_dist = dist.metadata.get_all("Requires-Dist") or []
        aio_reqs = [
            req for req in requires_dist
            if re.search(r"extra\s*==\s*['\"]aio['\"]", req)
        ]
        self.assertTrue(aio_reqs, "no requirement is tagged for the 'aio' extra")

        joined = " ".join(aio_reqs).lower()
        self.assertIn("azure-core", joined)
        self.assertIn("[aio]", joined)
        self.assertIn("1.30", joined)

    def test_azure_cosmos_aio_module_imports(self):
        # If the async module cannot be imported the file would already
        # have failed to load at the top, so this is a small explicit
        # confirmation that the symbol is available.
        self.assertTrue(callable(CosmosClient))


if __name__ == "__main__":
    unittest.main()


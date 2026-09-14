# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Tests that verify the ``aio`` extras are declared on the package."""

import re
import unittest
from importlib import metadata as importlib_metadata

import pytest
from packaging.requirements import Requirement
from packaging.version import Version


@pytest.mark.cosmosEmulator
class TestAioExtrasPackaging(unittest.TestCase):

    def test_aio_extras_declared_in_distribution_metadata(self):
        # The installed package must advertise the aio extra and pin it to
        # azure-core with the aio extra at version 1.30.0 or newer, so
        # installing with the aio extra pulls in the async transport.
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

        # Check the azure-core[aio] requirement allows version 1.30.0 or newer.
        # Asking the specifier whether an older version is allowed keeps the
        # check valid across future version bumps and catches any regression.
        core_req_str = next(
            req for req in aio_reqs if "azure-core" in req.lower()
        )
        # Drop the environment marker before parsing as a Requirement.
        core_req = Requirement(core_req_str.split(";", 1)[0].strip())
        self.assertNotIn(
            Version("1.29.99"), core_req.specifier,
            f"azure-core[aio] requirement allows versions older than 1.30.0: "
            f"{core_req.specifier!r}",
        )

    def test_azure_cosmos_aio_module_imports(self):
        # Keep this import local so metadata validation can still run
        # and report actionable failures even if async import breaks.
        from azure.cosmos.aio import CosmosClient  # noqa: F401
        self.assertTrue(callable(CosmosClient))


if __name__ == "__main__":
    unittest.main()

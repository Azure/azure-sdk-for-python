# `azure-messaging-webpubsubservice` tests

Tests for this package are disabled with `disable_` file name prefixes because the package is, at the time of writing,
inactive (as is reflected by the development status in the package's `setup.py` file:
`Development Status :: 7 - Inactive`). Removing this `disable_` prefix will allow tests to get collected by `pytest` --
at that point the `pytest_sessionfinish` method in `conftest.py` can be removed.

Tests should be refactored to use the Azure SDK test proxy when a new version of this package is developed. A migration
guide explains the difference between test proxy- and `vcrpy`-based tests, as well as how to transition to the former
from the latter: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md.

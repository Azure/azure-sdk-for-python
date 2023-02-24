# ESRP Release Process

Up till [this PR]() the azure-sdk-for-python team release packages to `PyPI` using our own PyPI account. Over time, this responsibility assumed by automation provided by the ESRP team.

This process change should not affect the release process whatsoever. For most releases, there will be no change in release experience. Owners will still queue an `internal` build for their service, then approve each individual package for release as necessary.

The primary visible effect of these release changes is that these packages will be published by the `Microsoft` pypi account, _not_  `azure-sdk` account that has been used till now.

## Break Glass - Yanking/Deleting

Contact the `python` team via email, teams, or ICM: `python@microsoft.com`.

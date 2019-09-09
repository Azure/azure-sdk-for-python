## Engineering System Assumptions, Gotchas, and Minutiae

1. All wheels are generated with influence from `setup.cfg` at the built package root. This means that for most of our packages, the `universal` flag is set within the `setup.cfg`.

```
[bdist_wheel]
universal=1
```

## Build

Build CI for `azure-sdk-for-python` essentially builds and tests packages in one of two methodologies.

### Individual Packages
1. Leverage `tox` to create wheel, install, and execute tests against newly installed wheel
2. Tests each package in isolation (outside of dev_requirements.txt dependencies + necessary `pylint` and `mypy`)

### Global Method

1. Install on packages (and their dev_requirements!) in one go.
2. Run `pytest <folder1>, pytest <folder2>` where folders correspond to package folders
    1. While all packages are installed alongside each other, each test run is individual to the package. This has the benefit of not allowing `packageA`'s `conftest.py` to mess with `packageB`'s environment.'

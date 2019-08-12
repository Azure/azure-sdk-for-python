# Contributing to Azure Python SDK

If you would like to become an active contributor to this project please
follow the instructions provided in [Microsoft Azure Projects Contribution Guidelines](http://azure.github.io/guidelines/).

## The Local Development Loop

The Azure SDK team's Python CI leverages the tool `tox` to distribute tests to virtual environments, handle test dependency installation, and coordinate tooling reporting during PR/CI builds. This means that a dev working locally can reproduce _exactly_ what the build machine is doing. 

< todo, put a placeholder diagram that shows that build ci executes the `tox` for each package that is being build >

[A Brief Overview of Tox](https://tox.readthedocs.io/en/latest/)

Traditionally, the `tox.ini` file for a package sits _alongside the setup.py_ in source code. The `azure-sdk-for-python` repo adheres to this same philosophy.

A given `tox.ini` works on the concept of `test environments`. A given test environment is a combination of:

1. An identifier
2. A targeted Python version 
    a. `tox` will default to base python executing the `tox` command if no Python environment is specified
3. (optionally) an OS platform

Internally `tox` leverages `virtualenv` to create each test environment's virtual environment. 

This means that once the `tox` workflow is in place, all tests will be executed _within a virtual environment._

To see the default environments from a specific `tox.ini` file, use the command `tox -l` in the same directory as the file itself.

> sdk-for-python/eng/tox> tox -l

```

linux-wheel_tests
macos-wheel_tests
windows-wheel_tests
sdist

```

### Example Usage of the Azure SDK For Python `tox.ini` Files

Basic usage of `tox` is:

1. `pip install tox`
2. `cd` to target package folder
3. run `tox`

However, take a look at the above environment list. Running just `tox` will result in a virtual environment for each of the above environment list! 

#### `dev` environment
This is the most straightforward environment. Installs a given package in `develop` mode.

#### `*wheel_tests` environments
Used for test execution across the spectrum of all the platforms we want to support. Maintained at a `platform specific` level just in case we run into platform-specific bugs.

* Installs the wheel, runs tests using the wheel

#### `sdist` environment
Used to install the development version of the package.

```
# both
\> tox -e py36-lint,py27-lint

# single
\> tox -e py27-lint

```

#### `sdist` environment
Used for the local dev loop.

* Installs package in editable mode
* Runs tests using the editable mode installation, not the wheel

```

\> tox -e sdist

```

## Code of Conduct
This project's code of conduct can be found in the
[CODE_OF_CONDUCT.md file](https://github.com/Azure/azure-sdk-for-python/blob/master/CODE_OF_CONDUCT.md)
(v1.4.0 of the http://contributor-covenant.org/ CoC).

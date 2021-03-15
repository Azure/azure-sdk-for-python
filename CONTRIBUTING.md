# Contributing to Azure Python SDK

If you would like to become an active contributor to this project please
follow the instructions provided in [Microsoft Azure Projects Contribution Guidelines](https://opensource.microsoft.com/collaborate/).

## Building and Testing

The Azure SDK team's Python CI leverages the tool `tox` to distribute tests to virtual environments, handle test dependency installation, and coordinate tooling reporting during PR/CI builds. This means that a dev working locally can reproduce _exactly_ what the build machine is doing. 

[A Brief Overview of Tox](https://tox.readthedocs.io/en/latest/)

#### A Monorepo and Tox in Harmony

Traditionally, the `tox.ini` file for a package sits _alongside the setup.py_ in source code. The `azure-sdk-for-python` necessarily does not adhere to this policy. There are over one-hundred packages contained here-in. That's a lot of `tox.ini` files to maintain!

Instead, the CI system leverages an tox plugin called `tox-monorepo`. This plugin allows `tox` to act as if the `tox.ini` is located in whatever directory you executed tox in!

#### Tox Environments

A given `tox.ini` works on the concept of `test environments`. A given test environment is a combination of:

1. An identifier (or identifiers)
2. A targeted Python version 
    1. `tox` will default to base python executing the `tox` command if no Python environment is specified
3. (optionally) an OS platform

Internally `tox` leverages `virtualenv` to create each test environment's virtual environment. 

This means that once the `tox` workflow is in place, all tests will be executed _within a virtual environment._

To see the default environments from a specific `tox.ini` file, use the command `tox -l` in the same directory as the file itself.

> sdk-for-python/eng/tox> tox -l

```

whl
sdist

```

Unfortunately, the command `tox -l` only returns the _default_ test builds. The common `tox.ini` file also supports `lint` and `mypy` environments.

### Example Usage of the common Azure SDK For Python `tox.ini` 

Basic usage of `tox` within this monorepo is:

1. `pip install tox tox-monorepo`
2. `cd` to target package folder
3. run `tox -c path/to/tox.ini`

The common `tox.ini` location is `eng/tox/tox.ini` within the repository.

If at any time you want to blow away the tox created virtual environments and start over, simply append `-r` to any tox invocation! 

#### Example `azure-core` mypy

1. `cd` to `sdk/core/azure-core`
2. Run `tox -e mypy -c ../../../eng/tox/tox.ini`

#### Example `azure-storage-blob` tests

1. `cd` to `sdk/storage/azure-storage-blob`
2. Execute `tox -c ../../../eng/tox/tox.ini`

Note that we didn't provide an `environment` argument for this example. Reason here is that the _default_ environment selected by our common `tox.ini` file is one that runs `pytest`.

#### `whl` environment
Used for test execution across the spectrum of all the platforms we want to support. Maintained at a `platform specific` level just in case we run into platform-specific bugs.

* Installs the wheel, runs tests using the wheel

```
\> tox -e whl -c <path to tox.ini>

```

#### `sdist` environment
Used for the local dev loop.

* Installs package in editable mode
* Runs tests using the editable mode installation, not the wheel

```

\> tox -e sdist -c <path to tox.ini>

```

#### `lint` environment
Pylint install and run.

```
\> tox -e lint -c <path to tox.ini>
```


#### `mypy` environment
Mypy install and run.

```
\> tox -e mypy -c <path to tox.ini>
```

### Custom Pytest Arguments

`tox` supports custom arguments, and the defined pytest environments within the common `tox.ini` also allow these. Essentially, separate the arguments you want passed to `pytest` by a `--` in your tox invocation.

[Tox Documentation on Positional Arguments](https://tox.readthedocs.io/en/latest/example/general.html#interactively-passing-positional-arguments)

**Example: Invoke tox, breaking into the debugger on failure**
`tox -e whl -c ../../../eng/tox/tox.ini -- --pdb`

### Performance Testing

SDK performance testing is supported via the custom `perfstress` framework. For full details on this framework, and how to write and run tests for an SDK - see the [perfstress tests documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/tools/azure-devtools/doc/perfstress_tests.md).

### More Reading

We maintain an [additional document](https://github.com/Azure/azure-sdk-for-python/blob/master/doc/eng_sys_checks.md) that has a ton of detail as to what is actually _happening_ in these executions.

### Dev Feed
Daily dev build version of Azure sdk packages for python are available and are uploaded to Azure devops feed daily. We have also created a tox environment to test a package against dev built version of dependent packages. Below is the link to Azure devops feed.
[`https://dev.azure.com/azure-sdk/public/_packaging?_a=feed&feed=azure-sdk-for-python`](https://dev.azure.com/azure-sdk/public/_packaging?_a=feed&feed=azure-sdk-for-python)

##### To install latest dev build version of a package
```
pip install <package-name> --extra-index-url https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple --pre
```

#### To Install a specific dev build version of a package
For e.g.
```
pip install azure-appconfiguration==1.0.0b6.dev20191205001 --extra-index-url https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple
```

To test a package being developed against latest dev build version of dependent packages:
a. cd to package root folder
b. run tox environment devtest

```
\> tox -e devtest -c <path to tox.ini>
```

This tox test( devtest) will fail if installed dependent packages are not dev build version.

## Code of Conduct
This project's code of conduct can be found in the
[CODE_OF_CONDUCT.md file](https://github.com/Azure/azure-sdk-for-python/blob/master/CODE_OF_CONDUCT.md)
(v1.4.0 of the https://contributor-covenant.org/ CoC).

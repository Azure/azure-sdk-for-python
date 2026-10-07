# Azure packaging

[comment]: # ( cspell:ignore myservice azuremyservice msvc MSRUSTUP )

> **Note:** This document covers legacy packaging using `setup.py`. New packages should use `pyproject.toml` instead. See the [`sdk/template/azure-template`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/template/azure-template) for the current package template.

## Native wheel builds in CI

`sdk_build` uses `cibuildwheel` when a package declares setuptools `ext_modules`
or a `[tool.cibuildwheel]` table in `pyproject.toml`. The latter supports
non-setuptools backends, including Maturin/PyO3. The package owns its wheel
matrix, backend requirements, and native build hooks.

Set `signBinaries: true` on the package's artifact entry in the service `ci.yml`
to enable Windows and macOS wheel builds and the existing binary-signing release
path. The platform resolver uses this artifact property, not package names.

Packages using the Microsoft Rust toolchain can opt in through
`archetype-sdk-client.yml`:

```yaml
extends:
  template: /eng/pipelines/templates/stages/archetype-sdk-client.yml
  parameters:
    ServiceDirectory: myservice
    InstallMsRustToolchain: true
    MsRustWorkingDirectory: $(Build.SourcesDirectory)/sdk/myservice/azure-myservice
    MsRustToolchainFeed: https://pkgs.dev.azure.com/azure-sdk/_packaging/<approved-rust-feed>/nuget/v3/index.json
    MsRustAdditionalTargets: aarch64-pc-windows-msvc
    Artifacts:
      - name: azure-myservice
        safeName: azuremyservice
        signBinaries: true
```

Replace `<approved-rust-feed>` with an approved organization-local feed that
provides the internal Rust toolchain. No prototype test feed is selected by
default. The working directory must contain `rust-toolchain.toml`.
The installer refuses to overwrite an existing Cargo configuration in its
`CARGO_HOME`; provide a clean build environment.
Rust installation is disabled by default and applies only to wheel-build jobs.
Opted-in jobs have a 240-minute timeout and a 210-minute package-build timeout;
other jobs keep their existing limits.

Linux wheels build inside manylinux containers. The package's `before-all` hook
must install the internal toolchain and configure Cargo source replacement
inside each container. The pipeline forwards `PIP_INDEX_URL`,
`MSRUSTUP_ACCESS_TOKEN`, `MSRUSTUP_FEED_URL`, and the
`CARGO_REGISTRIES_AZURE_SDK_FOR_RUST_PUBLIC_*` index, token, and credential-provider
variables. Credentials stay in the build environment, not checked-in files.
On Windows, `PYTHON_ARM64_LIB_DIR` points to the pre-provisioned ARM64 Python
import libraries; a package can use it as `PYO3_CROSS_LIB_DIR` for cross-compilation.

This opt-in does not provision Rust for source-installing test, documentation,
or analysis jobs. Prepare those jobs separately before enabling a Rust package,
and keep real source-distribution testing. Packages with a static
`[project].version` also need version synchronization with `_version.py` for
nightly builds. No package is activated by adding this shared support.

This article describes the recommendations for defining namespace packaging to release a package inside the `azure` namespace. Being inside the `azure` namespace means that a service `myservice` can be imported using:
```python
import azure.myservice
```

Namespace packaging is complicated in Python, here's a few reading if you still doubt it:
- https://packaging.python.org/guides/packaging-namespace-packages/
- https://www.python.org/dev/peps/pep-0420/
- https://github.com/pypa/sample-namespace-packages

Note:
While this article provides an example using setup.py, this can also be achieved with setup.cfg or other methods, as long as the constraints on the final wheels/sdist are met.

*This page has been updated to be Python 3 only packages as we do not recommend supporting Python 2 after January 1st 2022.* If you still want to support Python 2 for some reasons, there is a section at the bottom with some details (or you have the Github history, to read the page as it was on November 1st 2021).

# What are the constraints?

We want to build sdist and wheels in order to follow the following constraints:
- Solution should work with *recent* versions of pip and setuptools (not the very latest only, but not archaeology either)
- Wheels must work with Python 3.10+
- mixed dev installation and PyPI installation should be explicitly addressed

# What do I do in my files to achieve that

The minimal files to have:
- azure/\_\_init\_\_.py
- MANIFEST.in
- setup.py

The file "azure/\_\_init\_\_.py" must contain exactly this:
```python
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
```

Your MANIFEST.in must include the following line `include azure/__init__.py`.

Example:
```shell
include *.md
include LICENSE
include azure/__init__.py
recursive-include tests *.py
recursive-include samples *.py *.md
```
In your setup.py:

The "packages" section MUST EXCLUDE the `azure` package. Example:
```python
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
    ]),
```

Since the package is Python 3 only, you must notify it in the setup.py as well:
```python
    python_requires=">=3.10",
```

Example of a full setup.py
```python
#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import re
import os.path
from io import open
from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-keyvault"
PACKAGE_PPRINT_NAME = "KeyVault"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace('-', '/')
# a-b-c => a.b.c
namespace_name = PACKAGE_NAME.replace('-', '.')

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, 'version.py'), 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()
with open('HISTORY.rst', encoding='utf-8') as f:
    history = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description='Microsoft Azure {} Client Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=readme + '\n\n' + history,
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=3.10",
    zip_safe=False,
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
    ]),
    install_requires=[
        'msrest>=0.5.0',
        'msrestazure>=0.4.32,<2.0.0',
        'azure-common~=1.1',
    ],
)
```

This syntax works with setuptools >= 24.2.0 (July 2016) and pip >= 9.0 (Nov 2016), which is considered enough to support in 2021.

Since the package is Python 3 only, do NOT make this wheel universal. This usually means you should NOT have `universal=1` in the `setup.cfg`. It may mean you can completely remove the file if `universal` was the only configuration option inside.

# How can I check if my packages are built correctly?

- wheel file must NOT contain a `azure/__init__.py` file (you can open it with a zip util to check)
- wheel file name suffix is `py3-none-any`, and NOT `py2.py3-none-any`.
- sdist must contain a `azure/__init__.py` file that declares `azure` as a namespace package using the `pkgutil` syntax

# I already have a package that supports Python 2, can I get short version on how to udpate to Python 3 only?

- Remove "universal" from setup.cfg, or completely remove the file if it was the only option
- In setup.py:
  - Remove `extra_requires`
  - Add `python_requires=">=3.10",`
  - Remove the Python 2 and 3.5/3.6 classifiers
  - Add classifier `Programming Language :: Python :: 3 :: Only`
  - Remove the "azure" check if applicable (see next note)

# Note on checking old Azure packages

You may see code in `setup.py` looking like this:
```python
# azure v0.x is not compatible with this package
# azure v0.x used to have a __version__ attribute (newer versions don't)
try:
    import azure

    try:
        VER = azure.__version__  # type: ignore
        raise Exception(
            "This package is incompatible with azure=={}. ".format(VER) + 'Uninstall it with "pip uninstall azure".'
        )
    except AttributeError:
        pass
except ImportError:
    pass
```

This was to prevent some difficult update scenario 6 years ago, and can be safely removed from your setup.py

# Note on Python 2

The "extras_requires" section MUST include a conditional dependency on "azure-nspkg" for Python 2. Example:

```python
    extras_require={
        ":python_version<'3.0'": ['azure-nspkg'],
    }
```

An additional verification is that wheels installs `azure-nspkg` ONLY on Python 2.

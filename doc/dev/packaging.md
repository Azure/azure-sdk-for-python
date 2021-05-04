# Azure packaging

This article describes how to declare setup.py and all packaging information for packages inside the `azure` namespace

Namespace packaging is complicated in Python, here's a few reading if you still doubt it:
- https://packaging.python.org/guides/packaging-namespace-packages/
- https://www.python.org/dev/peps/pep-0420/
- https://github.com/pypa/sample-namespace-packages

This article describes the recommendation on how to define namespace packaging to release a package inside the `azure` namespace. Being inside the `azure` namespace meaning you have a service `myservice` that you want to import using:
```python
import azure.myservice
```

Note:
- This article is not about setup.py or setup.cfg or the right way to *write* the packaging, it's about what instructions you should use to achieve this. If you are fluent in setuptools, and prefer to write the suggestions in setup.cfg and not in setup.py, this is not a concern.

# What are the constraints?

We want to build sdist and wheels in order to follow the following constraints:
- Solution should work with *recent* versions of pip and setuptools (not the very latest only, but not archaeology either)
- Wheels must work with Python 2.7 and 3.6+
- easy-install scenario is a plus, but cannot be considered critical anymore
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

The "extras_requires" section MUST include a conditional dependency on "azure-nspkg" for Python 2. There is also a conditional dependency on "typing" for Python 3.5 because of the type-hinting for Python 3.5 and above. Example:

```python
    extras_require={
        ":python_version<'3.0'": ['azure-nspkg'],
        ":python_version<'3.5'": ['typing'],
    }
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
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
    extras_require={
        ":python_version<'3.0'": ['azure-nspkg'],
        ":python_version<'3.5'": ['typing'],
    }
)
```

This syntax works with setuptools >= 17.1 and pip >= 6.0, which is considered enough to support in 2019.

# How can I check if my packages are built correctly?

- wheels must NOT contain a `azure/__init__.py` file (you can open it with a zip util to check)
- wheels installs `azure-nskpg` ONLY on Python 2.
- sdist must contain a `azure/__init__.py` file that declares `azure` as a namespace package using the `pkgutil` syntax

#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import sys
import re
from pathlib import Path
from build_package import create_package

travis_tag = os.environ.get('TRAVIS_TAG')
if not travis_tag:
    print("TRAVIS_TAG environment variable is not present")
    sys.exit()

matching = re.match(r"^(?P<name>azure[a-z\-]*)_(?P<version>[.0-9]+[rc0-9]*)$", travis_tag)
if not matching:
    print("TRAVIS_TAG is not '<package_name> <version>' (tag is: {})".format(travis_tag))
    sys.exit()

name, version = matching.groups()
create_package(name, '../dist')

print("Produced:\n{}".format(list(Path('./dist').glob('*'))))

pattern = "*{}*".format(version)
packages = list(Path('./dist').glob(pattern))
if not packages:
    sys.exit("Package version does not match tag {}, abort".format(version))
print("Package created as expected and will be pushed to {}".format(os.environ.get("PYPI_SERVER", "default PyPI server")))

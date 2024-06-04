#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import os
from tempfile import mkstemp

import pytest


@pytest.fixture
def temp_file_path():
    f, path = mkstemp()
    os.close(f)
    yield path
    try:
        os.unlink(path)
    except:
        pass

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Test violates do-not-import-legacy-six
from six.moves import range

def legacy_operation() -> range:
    return range(10)

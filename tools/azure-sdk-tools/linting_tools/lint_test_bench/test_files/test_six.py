# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Test violates do-not-import-legacy-six
import six

def legacy_operation() -> range:
    return six.moves.range(10)

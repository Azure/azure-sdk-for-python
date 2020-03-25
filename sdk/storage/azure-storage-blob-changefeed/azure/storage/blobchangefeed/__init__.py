# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.paging import ItemPaged
from ._change_feed_client import ChangeFeedClient


__all__ = [
    'ChangeFeedClient',
    'ItemPaged'
]

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

"""
The contents of modules within this directory are part of the AnyIO library by Alex Grönholm,
used here without any modification.

https://github.com/agronholm/anyio

Currently using version 1.3.0, retrieved 27-03-2020.
https://github.com/agronholm/anyio/releases/tag/1.3.0
"""

try:
    from anyio import create_task_group, sleep, connect_tcp, create_capacity_limiter
except ImportError:
    from ._asyncio import create_task_group, sleep, connect_tcp, create_capacity_limiter

__all__ = [
    'create_task_group',
    'sleep',
    'connect_tcp',
    'create_capacity_limiter'
]
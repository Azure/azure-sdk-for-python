import os
from subprocess import check_call
from .generation import prepare_and_test_optional
from .managed_virtual_env import ManagedVirtualEnv

from typing import Optional

# todo rename managed_virtual_env to virtual_env and move below functions there

__all__ = ["prepare_and_test_optional", "ManagedVirtualEnv"]

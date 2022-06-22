# Test for CheckNamingMismatchGeneratedCode

from something import Something
from something2 import something2 as somethingTwo

__all__ = (
    Something,
    somethingTwo, #pylint: disable=naming-mismatch
)

from . import _range as prange
from typing import Any, Dict, List, Optional, Union, Iterable, cast, overload  # pylint: disable=unused-import
from .partition_key import _Undefined, _Empty, PartitionKey
MaximumExclusiveEffectivePartitionKey = 0xFF
MinimumInclusiveEffectivePartitionKey = 0x00

def GetEPKRangeForPrefixPartitionKey(partitionKeyDefinition : PartitionKey) -> prange.Range:
    minEPK = GetEffectivePartitionKeyString(partitionKeyDefinition, False);
    maxEPK = minEPK + MaximumExclusiveEffectivePartitionKey;
    return prange.Range(minEPK, maxEPK)

def GetEffectivePartitionKeyForHashPartitioning():
    pass

def GetEffectivePartitionKeyForHashPartitioningV2():
    pass

def GetEffectivePartitionKeyForMultiHashPartitioningV2():
    pass

def ToHexEncodedBinaryString(path: Union[str, list]) -> str:
    pass

def GetEffectivePartitionKeyString(partitionKeyDefinition : PartitionKey, strict: bool) -> str:
    if type(partitionKeyDefinition) == _Empty:
        return MinimumInclusiveEffectivePartitionKey
    if partitionKeyDefinition.kind == "Hash":
        if partitionKeyDefinition.version == 1:
            GetEffectivePartitionKeyForHashPartitioning()
        elif partitionKeyDefinition.version == 2:
            GetEffectivePartitionKeyForHashPartitioningV2()
    elif partitionKeyDefinition.kind == "MultiHash":
        GetEffectivePartitionKeyForMultiHashPartitioningV2()
    else:
        return ToHexEncodedBinaryString(partitionKeyDefinition.paths)


#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Internal class for partition key range implementation in the Azure Cosmos database service.
"""

class _PartitionKeyRange(object):
    """Partition Key Range Constants"""
    MinInclusive = 'minInclusive'
    MaxExclusive = 'maxExclusive'
    Id = 'id'
    Parents = 'parents'

class _Range(object):
    """description of class"""
    
    MinPath = 'min'
    MaxPath = 'max'
    IsMinInclusivePath = 'isMinInclusive'
    IsMaxInclusivePath = 'isMaxInclusive'
        
    def __init__(self, range_min, range_max, isMinInclusive, isMaxInclusive):
        if range_min is None:
            raise ValueError("min is missing")
        if range_max is None:
            raise ValueError("max is missing")

        self.min = range_min
        self.max = range_max
        self.isMinInclusive = isMinInclusive
        self.isMaxInclusive = isMaxInclusive
        
    def contains(self, value):
        minToValueRelation = self.min > value
        maxToValueRelation = self.max > value
        return ((self.isMinInclusive and minToValueRelation <= 0) or \
                    (not self.isMinInclusive and minToValueRelation < 0)) \
               and ((self.isMaxInclusive and maxToValueRelation >= 0) \
                    or (not self.isMaxInclusive and maxToValueRelation > 0))

    @classmethod
    def PartitionKeyRangeToRange(cls, partition_key_range):
        self = cls(partition_key_range[_PartitionKeyRange.MinInclusive], partition_key_range[_PartitionKeyRange.MaxExclusive],
                   True, False)
        return self
    
    @classmethod
    def ParseFromDict(cls, range_as_dict):
        self = cls(range_as_dict[_Range.MinPath], range_as_dict[_Range.MaxPath], range_as_dict[_Range.IsMinInclusivePath], range_as_dict[_Range.IsMaxInclusivePath])
        return self
    
    def isSingleValue(self):
        return self.isMinInclusive and self.isMaxInclusive and self.min == self.max

    def isEmpty(self):
        return (not (self.isMinInclusive and self.isMaxInclusive)) and self.min == self.max
    
    def __hash__(self):
        return hash((self.min, self.max, self.isMinInclusive, self.isMaxInclusive))

    def __str__(self):

        return (('[' if self.isMinInclusive else '(') + str(self.min) + ',' + str(self.max) + (']' if self.isMaxInclusive else ')'))

    def __eq__(self, other):
        return (self.min == other.min) and (self.max == other.max) \
                and (self.isMinInclusive == other.isMinInclusive) \
                and (self.isMaxInclusive == other.isMaxInclusive)
    
    
    @staticmethod
    def _compare_helper(a,b):
        # python 3 compatible
        return (a > b) - (a < b)
        
    @staticmethod
    def overlaps(range1, range2):

        if range1 is None or range2 is None: return False
        if range1.isEmpty() or range2.isEmpty(): return False
            
        cmp1 = _Range._compare_helper(range1.min, range2.max)
        cmp2 = _Range._compare_helper(range2.min, range1.max)

        if (cmp1 <= 0 or cmp2 <= 0):
            if ((cmp1 == 0 and not(range1.isMinInclusive and range2.isMaxInclusive)) or (cmp2 == 0 and not(range2.isMinInclusive and range1.isMaxInclusive))):
                return False
            return True
        return False

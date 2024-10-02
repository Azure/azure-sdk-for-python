# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from functools import reduce
from typing import List


def list_sum(lst: List[float]) -> float:
    return reduce(lambda a, b: a+b, lst)


def list_mean(lst: List[float]) -> float:
    return list_sum(lst)/len(lst)


def list_mean_nan_safe(lst: List[float]) -> float:
    return list_mean([l for l in lst if not math.isnan(l)])

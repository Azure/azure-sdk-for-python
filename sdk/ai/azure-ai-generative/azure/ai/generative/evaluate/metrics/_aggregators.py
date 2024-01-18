# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import numpy as np


def mean(*, values, **kwargs):
    value = np.nanmean(values)
    return {"mean": value}


def median(*, values, **kwargs):
    value = np.nanmedian(values)
    return {"median": value}


def pass_rate(*, values, **kwargs):
    """
    Pass rate calculates number of row in dataset that have non NaN value
    """
    value = len(values) - np.count_nonzero(np.isnan(values))
    return {f"pass_rate": value}


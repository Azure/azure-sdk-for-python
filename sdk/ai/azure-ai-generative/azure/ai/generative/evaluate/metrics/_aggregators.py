# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import numpy as np


def mean(*, values, **kwargs):
    metric_name = kwargs.get("metric_name")
    value = np.nanmean(values)
    return {f"mean_{metric_name}": value}


def median(*, values, **kwargs):
    metric_name = kwargs.get("metric_name")
    value = np.nanmedian(values)
    return {f"median_{metric_name}": value}


def pass_rate(*, values, **kwargs):
    """
    Pass rate calculates number of row in dataset that have non NaN value
    """
    metric_name = kwargs.get("metric_name")
    value = len(values) - np.count_nonzero(np.isnan(values))
    return {f"pass_rate_{metric_name}": value}



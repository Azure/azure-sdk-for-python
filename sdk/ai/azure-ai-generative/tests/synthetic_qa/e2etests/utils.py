# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import re
import string
from collections import Counter
from typing import List

logger = logging.getLogger(__name__)


def normalize(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    s = s.lower()
    exclude = set(string.punctuation)
    s = "".join(char for char in s if char not in exclude)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = " ".join(s.split())
    return s


def f1_score(prediction: str, ground_truth: str):
    prediction_tokens = normalize(prediction).split()
    ground_truth_tokens = normalize(ground_truth).split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def find_closest_prediction(predictions: List[str], ground_truth: str):
    best_f1 = -1
    closest_pred = None
    for pred in predictions:
        f1 = f1_score(pred, ground_truth)
        if f1 >= best_f1:
            best_f1 = f1
            closest_pred = pred
    return closest_pred

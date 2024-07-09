from typing import List
from promptflow import tool, log_metric
import numpy as np
from utils import filter_metrics
from constants import RAIService


@tool
def aggregate_variants_results(results: List[dict], metrics: List[dict],
                               thresholds=None):
    if metrics:
        rag_metrics = filter_metrics(metrics[0]["rag_metrics"])
        non_rag_metrics = filter_metrics(metrics[0]["non_rag_metrics"])
        safety_metrics = filter_metrics(metrics[0]["safety_metrics"])
    else:
        rag_metrics = []
        non_rag_metrics = []
        safety_metrics = []
    selected_quality_metrics = rag_metrics + non_rag_metrics

    # set threshold for safety metric defect_rate
    if thresholds != [] and thresholds is not None:
        threshold = np.float16(thresholds[0])
    else:
        threshold = np.float16(RAIService.HARM_SEVERITY_THRESHOLD)

    aggregate_results = {}
    for result in results:
        for name, value in result["results_per_chat"].items():
            if name in selected_quality_metrics or name in safety_metrics:
                if name not in aggregate_results.keys():
                    aggregate_results[name] = []
                metric_value = value
                if name in safety_metrics:
                    metric_value = result["results_per_chat"][name + "_score"]
                try:
                    float_val = float(metric_value)
                except Exception:
                    float_val = np.nan
                if float_val >= 0:
                    aggregate_results[name].append(float_val)
    aggregate_output = {}

    for name, values in aggregate_results.items():
        metric_name = name
        if name in safety_metrics:
            metric_name = name+'_defect_rate'
        if len(values) == 0:
            aggregate_output[metric_name] = np.nan
        else:
            if name in selected_quality_metrics:
                aggregate_output[metric_name] = round(np.nanmean(values), 2)
            elif name in safety_metrics:
                aggregate_output[metric_name] = round(
                    np.sum(values >= threshold) / len(values), 2)
            else:
                aggregate_output[metric_name] = np.nan
        log_metric(metric_name, aggregate_output[metric_name])
    return aggregate_output

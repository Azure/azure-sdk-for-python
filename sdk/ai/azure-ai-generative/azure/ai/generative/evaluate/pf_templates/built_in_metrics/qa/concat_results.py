from promptflow import tool
import constants
import numpy as np


def default_safety_results():
    supported_metrics = constants.Metric.CONTENT_HARM_METRICS
    result = {}
    for metric_name in supported_metrics:
        result[metric_name] = np.nan
        result[metric_name + "_score"] = np.nan
        result[metric_name + "_reason"] = np.nan
    return result


def default_gpt_results():
    supported_metrics = constants.Metric.QUALITY_METRICS
    result = {}
    for metric_name in supported_metrics:
        if metric_name != "gpt_groundedness":
            result[metric_name] = np.nan
    return result


def default_groundedness_results():
    return {"gpt_groundedness": np.nan,
            "gpt_groundedness_reason": np.nan
            }


@tool
def concat_results(selected_metrics: dict,
                   quality_results: dict = None,
                   safety_results: dict = None,
                   groundedness_results: dict = None) -> dict:
    if quality_results:
        concated_results = quality_results.copy()
    else:
        concated_results = default_gpt_results()
    if groundedness_results:
        concated_results.update(groundedness_results)
    else:
        concated_results.update(default_groundedness_results())
    if safety_results:
        concated_results.update(safety_results)
    else:
        concated_results.update(default_safety_results())

    return concated_results

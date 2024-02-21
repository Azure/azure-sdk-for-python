from promptflow import tool
import constants
import numpy as np

def default_safety_results():
    supported_metrics = constants.Metric.CONTENT_HARM_METRICS
    result = {}
    for metric_name in supported_metrics:
        result[metric_name] = np.nan
        result[metric_name + "_score"] = np.nan
        result[metric_name + "_reasoning"] = np.nan
    return result

def default_quality_results():
    supported_metrics = constants.Metric.QUALITY_METRICS
    result = {}
    for metric_name in supported_metrics:
        result[metric_name] = np.nan
    return result


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def concat_results(selected_metrics: dict, quality_results: dict = None, safety_results: dict = None) -> dict:
    if quality_results:
        concated_results = quality_results.copy()
    else:
        concated_results = default_quality_results()
    if safety_results:
        concated_results.update(safety_results)
    else:
        concated_results.update(default_safety_results())

    return concated_results
    

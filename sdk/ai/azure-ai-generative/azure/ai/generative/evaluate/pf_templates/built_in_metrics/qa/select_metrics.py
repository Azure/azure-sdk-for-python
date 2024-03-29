from promptflow import tool
import constants


def select_metrics_from_metric_list(user_selected_metrics: list,
                                    supported_metrics: tuple):
    metric_dict = {}
    for metric in supported_metrics:
        if metric in user_selected_metrics or len(user_selected_metrics) == 0:
            metric_dict[metric] = True
        else:
            metric_dict[metric] = False
    return metric_dict


@tool
def select_metrics(metrics: str) -> dict:
    supported_quality_metrics = constants.Metric.QUALITY_METRICS
    supported_safety_metrics = \
        constants.Metric.CONTENT_HARM_METRICS
    user_selected_metrics = [metric.strip()
                             for metric in metrics.split(',') if metric]
    metric_selection_dict = {}
    metric_selection_dict['quality_metrics'] = select_metrics_from_metric_list(
        user_selected_metrics, supported_quality_metrics)
    metric_selection_dict['safety_metrics'] = select_metrics_from_metric_list(
        user_selected_metrics, supported_safety_metrics)
    return metric_selection_dict

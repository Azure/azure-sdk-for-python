from promptflow import tool


def select_metrics_from_metric_list(user_selected_metrics: list,
                                    supported_metrics: tuple):
    metric_selection_dict = {}
    for metric in supported_metrics:
        if metric in user_selected_metrics:
            metric_selection_dict[metric] = True
        else:
            metric_selection_dict[metric] = False
    return metric_selection_dict


@tool
def select_metrics(metrics: str) -> str:
    import constants
    supported_rag_metrics = constants.RAG_EVALUATION_SET
    supported_non_rag_metrics = constants.NON_RAG_EVALUATION_SET
    supported_safety_metrics = constants.CONTENT_HARM_METRICS
    user_selected_metrics = [metric.strip()
                             for metric in metrics.split(',') if metric]
    metric_selection_dict = {}
    metric_selection_dict["rag_metrics"] = select_metrics_from_metric_list(
        user_selected_metrics, supported_rag_metrics)
    metric_selection_dict["non_rag_metrics"] = select_metrics_from_metric_list(
        user_selected_metrics, supported_non_rag_metrics)
    metric_selection_dict["safety_metrics"] = select_metrics_from_metric_list(
        user_selected_metrics, supported_safety_metrics)

    return metric_selection_dict

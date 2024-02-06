from promptflow import tool

def select_metrics_from_metric_list(user_selected_metrics: list, supported_metrics: tuple):
    metric_selection_dict = {}
    for metric in supported_metrics:
        if metric in user_selected_metrics:
            metric_selection_dict[metric] = True
        else:
            metric_selection_dict[metric] = False
    return metric_selection_dict


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def select_metrics(metrics: str) -> str:
    from constants import RAG_EVALUATION_SET, NON_RAG_EAVLUATION_SET, CONTENT_HARM_METRICS
    supported_rag_metrics = RAG_EVALUATION_SET
    supported_non_rag_metrics = NON_RAG_EAVLUATION_SET
    supported_safety_metrics = CONTENT_HARM_METRICS
    user_selected_metrics = [metric.strip() for metric in metrics.split(',') if metric]
    metric_selection_dict = {}
    metric_selection_dict["rag_metrics"] = select_metrics_from_metric_list(user_selected_metrics,
                                                    supported_rag_metrics)
    metric_selection_dict["non_rag_metrics"] = select_metrics_from_metric_list(user_selected_metrics,
                                                    supported_non_rag_metrics)
    metric_selection_dict["safety_metrics"] = select_metrics_from_metric_list(user_selected_metrics, 
                                                    supported_safety_metrics)
    
    return metric_selection_dict

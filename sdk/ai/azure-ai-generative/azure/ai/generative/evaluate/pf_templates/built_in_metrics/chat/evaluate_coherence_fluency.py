from promptflow import tool
from azureml.metrics import compute_metrics, constants
from promptflow.connections import AzureOpenAIConnection
from utils import get_openai_parameters, filter_metrics


@tool
def evaluate_coherence_fluency(parsed_qa: dict,
                               connection: AzureOpenAIConnection,
                               deployment_name: str,
                               selected_metrics: dict):
    openai_params = get_openai_parameters(connection,
                                          deployment_name)

    metrics_config = {
     "questions": parsed_qa["questions"],
     "openai_params": openai_params
    }
    metrics = filter_metrics(selected_metrics["non_rag_metrics"])

    if len(metrics) == 0:
        return None

    use_chat_completion_api = True

    # Note : length of lists of y_test, y_pred,
    # questions, contexts should be equal
    result = compute_metrics(
        task_type=constants.Tasks.QUESTION_ANSWERING,
        y_pred=parsed_qa["answers"],
        metrics=metrics,
        use_chat_completion_api=use_chat_completion_api,
        **metrics_config)
    for metric in metrics:
        if not result["metrics"]["mean_" + metric] >= 0:
            use_chat_completion_api = not use_chat_completion_api
            break
    if use_chat_completion_api is False:
        result = compute_metrics(
            task_type=constants.Tasks.QUESTION_ANSWERING,
            y_pred=parsed_qa["answers"],
            metrics=metrics,
            use_chat_completion_api=use_chat_completion_api,
            **metrics_config)
    return result

from promptflow import tool
from azureml.metrics import compute_metrics, constants
from promptflow.connections import AzureOpenAIConnection
from utils import get_openai_parameters, filter_metrics

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def evaluate_coherence_fluency(parsed_qa: dict, connection: AzureOpenAIConnection, deployment_name: str, selected_metrics: dict):
    openai_params = get_openai_parameters(connection, deployment_name)

    metrics_config = {
     "questions" : parsed_qa["questions"],
     "openai_params" : openai_params
    }
    metrics = filter_metrics(selected_metrics["non_rag_metrics"])#["gpt_fluency", "gpt_coherence"]

    if len(metrics) == 0:
        return None

    # Note : length of lists of y_test, y_pred, questions, contexts should be equal
    result = compute_metrics(task_type=constants.Tasks.QUESTION_ANSWERING, 
                         y_pred=parsed_qa["answers"],
                         metrics = metrics,
                         **metrics_config)
    return result                
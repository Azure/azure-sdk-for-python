from promptflow.connections import AzureOpenAIConnection
import constants
import numpy as np
from azureml.metrics.common import _validation
from azureml.metrics.common.contract import Contract


def get_openai_parameters(connection: AzureOpenAIConnection,
                          deployment_name: str) -> dict:
    openai_params = {
        "api_version": connection['api_version'],
        "api_base": connection['api_base'],
        "api_type": "azure",
        "api_key": connection['api_key'],
        "deployment_id": deployment_name
    }
    return openai_params


def filter_metrics(selected_metrics):
    return [metric for metric in selected_metrics
            if selected_metrics[metric]]


def get_cred():
    from mlflow.tracking import MlflowClient
    import mlflow

    # check if tracking_uri is set. if False, return None
    if not mlflow.is_tracking_uri_set():
        return None

    mlflow_client = MlflowClient()
    cred = mlflow_client._tracking_client.store.get_host_creds()
    cred.host = cred.host.replace(
        "mlflow/v2.0", "mlflow/v1.0").replace("mlflow/v1.0", "raisvc/v1.0")
    return cred


def validate_annotation_task(task_type: str) -> bool:
    supported_annotation_task = [constants.Tasks.CONTENT_HARM]
    if task_type in supported_annotation_task:
        return True
    else:
        return False


def get_supported_metrics(task_type):
    task_options = {
        constants.Tasks.CONTENT_HARM: constants.Metric.CONTENT_HARM_METRICS,
        constants.Tasks.GROUNDEDNESS: constants.Metric.GROUNDEDNESS_METRICS
    }
    result = task_options.get(task_type, None)
    return result


def get_harm_severity_level(harm_score: int) -> str:
    HAMR_SEVERITY_LEVEL_MAPPING = {constants.HarmSeverityLevel.VeryLow: [0, 1],
                                   constants.HarmSeverityLevel.Low: [2, 3],
                                   constants.HarmSeverityLevel.Medium: [4, 5],
                                   constants.HarmSeverityLevel.High: [6, 7]
                                   }
    if harm_score == np.nan or harm_score is None:
        return np.nan
    for harm_level, harm_score_range in HAMR_SEVERITY_LEVEL_MAPPING.items():
        if harm_score >= harm_score_range[0] and\
           harm_score <= harm_score_range[1]:
            return harm_level.value
    return np.nan


def is_conversation_valid(chat: list[dict]) -> bool:
    reference_code = "validate_conversation"
    name = "chat_format"
    # check if role and content keys exist in every turn
    _validation._check_chat_conversation(
        [chat], name, reference_code=reference_code)
    return True


def is_conversation_valid_with_context(chat: list[dict]) -> bool:
    reference_code = "validate_conversation"
    name = "chat_context_format"

    # check if context/documents keys exist for rag evaluation
    for turn_num, each_turn in enumerate(chat):
        # to accept legacy rag_evaluation format:
        # [{"user": {"content": "<user_content>"},
        #  "assistant": {"content": "<assistang_content>"},
        #  "retrieved_documents": "<retrieved_documents>"}]
        if "user" in each_turn and "assistant" in each_turn:
            Contract.assert_true(
                "retrieved_documents" in each_turn,
                message="Please ensure to have retrieved_documents key \
                        in each turn for rag_evaluation."
                        + " Please check turn_number: {}".format(turn_num),
                target=name, log_safe=True,
                reference_code=reference_code)
        elif "role" in each_turn and each_turn["role"] == "assistant":
            # if "context" not in each_turn:
            Contract.assert_true(
                "context" in each_turn,
                message="Please ensure to have context key \
                        in assistant turn for rag_evaluation."
                        + " Please check turn_number: {}".format(turn_num),
                target=name, log_safe=True,
                reference_code=reference_code)
            if "context" in each_turn:
                Contract.assert_true(
                    "citations" in each_turn["context"],
                    message="Please ensure to have citations key \
                            in assistant turn context for rag_evaluation."
                            + " Please check turn_number: {}".format(turn_num),
                    target=name, log_safe=True,
                    reference_code=reference_code)

    return True

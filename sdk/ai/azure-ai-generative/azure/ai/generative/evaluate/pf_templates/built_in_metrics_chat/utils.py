from promptflow.connections import AzureOpenAIConnection
import constants

def get_openai_parameters(connection: AzureOpenAIConnection, deployment_name: str) -> dict:
    openai_params = {
        "api_version": connection['api_version'],
        "api_base": connection['api_base'],
        "api_type": "azure",
        "api_key" : connection['api_key'],
        "deployment_id": deployment_name
    }
    return openai_params

def filter_metrics(selected_metrics):
    return [metric for metric in selected_metrics if selected_metrics[metric]]

def get_cred():
    from mlflow.tracking import MlflowClient
    import mlflow
    
    ### check if tracking_uri is set. if False, return None
    if not mlflow.is_tracking_uri_set():
        return None
    
    mlflow_client = MlflowClient()
    cred = mlflow_client._tracking_client.store.get_host_creds()  # pylint: disable=protected-access
    cred.host = cred.host.replace("mlflow/v2.0", "mlflow/v1.0").replace("mlflow/v1.0", "raisvc/v1.0")
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
from promptflow import tool
import mlflow
from mlflow.utils.rest_utils import http_request
from utils import get_cred, is_valid_string


def is_service_available():
    try:
        cred = get_cred()
        cred.host = cred.host.split("/subscriptions")[0]

        response = http_request(
                host_creds=cred,
                endpoint="/meta/version",
                method="GET"
            )
        if response.status_code != 200:
            print("RAI service is not available in this region.")
            return False
        else:
            return True
    except Exception:
        print("RAI service is not available in this region.")
        return False

def is_tracking_uri_set():
    if not mlflow.is_tracking_uri_set():
        print("tracking_uri is not set")
        return False
    else:
        return True

def is_safety_metric_selected(selected_metrics: dict) -> bool:
    selected_safety_metrics = selected_metrics["safety_metrics"]
    for metric in selected_safety_metrics:
        if selected_safety_metrics[metric]:
            return True
    print("no safety_metrics are selected.")
    return False

def is_groundedness_metric_selected(selected_metrics: dict) -> bool:
    return selected_metrics["quality_metrics"]["gpt_groundedness"]

def is_input_valid_for_safety_metrics(question: str, answer: str):
    if is_valid_string(question) and is_valid_string(answer):
        return True 
    else:
        print("Input is not valid for safety metrics evaluation")
        return False 


# check if RAI service is avilable in this region. If not, return False.
# check if tracking_uri is set. If not, return False
# if tracking_rui is set, check if any safety metric is selected. 
# if no safety metric is selected, return False
@tool
def validate_safety_metric_input(
        selected_metrics: dict, 
        question: str, 
        answer: str,
        context: str = None) -> dict:
    service_available = is_service_available()
    tracking_uri_set = is_tracking_uri_set()
    input_valid_for_safety_metrics = is_input_valid_for_safety_metrics(question, answer)

    content_harm_service = is_safety_metric_selected(selected_metrics) \
        and service_available and tracking_uri_set \
        and is_input_valid_for_safety_metrics(question, answer)
    
    groundedness_service = is_groundedness_metric_selected(selected_metrics) \
        and service_available and tracking_uri_set
    
    return {"content_harm_service": content_harm_service,
            "groundedness_service": groundedness_service}
    
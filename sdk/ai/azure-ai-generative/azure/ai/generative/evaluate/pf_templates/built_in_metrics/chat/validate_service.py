from promptflow import tool
import mlflow
from mlflow.utils.rest_utils import http_request
from utils import get_cred

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
        return False

def is_tracking_uri_set():
    if not mlflow.is_tracking_uri_set():
        print("tracking_uri is not set")
        return False
    else:
        return True

def is_safety_metrics_selected(selected_metrics):
    for metric in selected_metrics["safety_metrics"]:
        if selected_metrics["safety_metrics"][metric]:
            return True
    print("No safety metrics are selected.")
    return False


# check if RAI service is avilable in this region. If not, return False.
# check if tracking_uri is set. If not, return False
# if tracking_rui is set, check if any safety metric is selected. 
# if no safety metric is selected, return False
@tool
def validate_safety_metric_input(selected_metrics: dict) -> dict:
    return is_safety_metrics_selected(selected_metrics) and \
            is_service_available() and \
            is_tracking_uri_set()
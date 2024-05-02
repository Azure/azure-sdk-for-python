from promptflow import tool
import mlflow
from mlflow.utils.rest_utils import http_request
from utils import get_cred, is_conversation_valid


def is_service_available(flight: bool):
    content_harm_service = False
    groundedness_service = False
    try:
        cred = get_cred()

        response = http_request(
            host_creds=cred,
            endpoint="/checkannotation",
            method="GET",
        )

        if response.status_code != 200:
            print("Fail to get RAI service availability in this region.")
            print("Response_code: %d" % response.status_code)
        else:
            available_service = response.json()
            if "content harm" in available_service:
                content_harm_service = True
            else:
                print("RAI service is not available in this region.")
            if "groundedness" in available_service and flight:
                groundedness_service = True
            if not flight:
                print("GroundednessServiceFlight is off.")
            if  "groundedness" not in available_service:
                print("AACS service is not available in this region.")
    except Exception:
        print("Failed to call checkannotation endpoint.")
    return {"content_harm_service": content_harm_service,
            "groundedness_service": groundedness_service
            }


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


def is_groundedness_metric_selected(selected_metrics: dict) -> bool:
    if not selected_metrics["rag_metrics"]["gpt_groundedness"]:
        print("gpt_groundedness is not selected.")
    return selected_metrics["rag_metrics"]["gpt_groundedness"]


def is_chat_valid(chat) -> bool:
    try:
        is_valid_chat_format = is_conversation_valid(chat)
    except Exception:
        print("The chat format is not valid for safety metrics")
        is_valid_chat_format = False
    return is_valid_chat_format


# check if RAI service is avilable in this region. If not, return False.
# check if tracking_uri is set. If not, return False
# if tracking_rui is set, check if any safety metric is selected.
# if no safety metric is selected, return False
@tool
def validate_safety_metric_input(
        selected_metrics: dict,
        chat: [dict],
        validate_chat_result: dict,
        flight: bool = True) -> dict:
    tracking_uri_set = is_tracking_uri_set()
    service_available = is_service_available(flight)
    valid_chat = is_chat_valid(chat)
    groundedness_selected = is_groundedness_metric_selected(selected_metrics)
    content_harm_service = is_safety_metrics_selected(selected_metrics) \
        and service_available["content_harm_service"] and tracking_uri_set\
        and valid_chat
    groundedness_service = groundedness_selected \
        and service_available["groundedness_service"] and tracking_uri_set\
        and valid_chat and validate_chat_result['rag_metrics']
    groundedness_prompt = groundedness_selected \
        and (not service_available["groundedness_service"]) \
        and valid_chat and validate_chat_result['rag_metrics']
    return {"content_harm_service": content_harm_service,
            "groundedness_service": groundedness_service,
            "groundedness_prompt": groundedness_prompt}

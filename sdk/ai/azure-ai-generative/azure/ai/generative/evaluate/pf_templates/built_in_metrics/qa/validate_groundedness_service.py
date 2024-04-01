from promptflow import tool
import mlflow
from mlflow.utils.rest_utils import http_request
from utils import get_cred


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
            # check if content harm service is avilable
            if "content harm" in available_service:
                content_harm_service = True
            else:
                print("Content harm service is not available in this region.")
            # check if groundedness service is avilable
            if "groundedness" in available_service and flight:
                groundedness_service = True
            if not flight:
                print("GroundednessServiceFlight is off.")
            if "groundedness" not in available_service:
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


def is_safety_metric_selected(selected_metrics: dict) -> bool:
    selected_safety_metrics = selected_metrics["safety_metrics"]
    for metric in selected_safety_metrics:
        if selected_safety_metrics[metric]:
            return True
    print("no safety_metrics are selected.")
    return False


def is_groundedness_metric_selected(selected_metrics: dict) -> bool:
    if not selected_metrics["quality_metrics"]["gpt_groundedness"]:
        print("gpt_groundedness is not selected.")
    return selected_metrics["quality_metrics"]["gpt_groundedness"]


# check if RAI service is avilable in this region. If not, return False.
# check if tracking_uri is set. If not, return False
# if tracking_rui is set, check if any safety metric is selected.
# if no safety metric is selected, return False
@tool
def validate_safety_metric_input(
        selected_metrics: dict,
        validate_input_result: dict,
        flight: bool = True,
        ) -> dict:
    tracking_uri_set = is_tracking_uri_set()
    service_available = is_service_available(flight)
    safety_metrics_selected = is_safety_metric_selected(selected_metrics)
    gpt_groundedness_selected = is_groundedness_metric_selected(
        selected_metrics)

    content_harm_service = safety_metrics_selected \
        and service_available["content_harm_service"] and tracking_uri_set \
        and validate_input_result["safety_metrics"]

    groundedness_service = gpt_groundedness_selected\
        and validate_input_result["gpt_groundedness"] and tracking_uri_set \
        and service_available["groundedness_service"]

    groundedness_prompt = gpt_groundedness_selected \
        and validate_input_result["gpt_groundedness"] \
        and (not service_available["groundedness_service"])

    if not validate_input_result["gpt_groundedness"] \
            and gpt_groundedness_selected:
        print("Input for gpt_groundedness is not valid")

    if not validate_input_result["safety_metrics"] and safety_metrics_selected:
        print("Input for safety metrics evaluation is not valid")

    return {"content_harm_service": content_harm_service,
            "groundedness_service": groundedness_service,
            "groundedness_prompt": groundedness_prompt
            }

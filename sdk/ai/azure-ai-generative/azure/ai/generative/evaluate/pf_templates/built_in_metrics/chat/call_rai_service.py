from promptflow import tool
from rai_client import RAIServiceHandler


@tool
def call_rai_service(request_body: dict) -> dict:
    service_handler = RAIServiceHandler()
    annotation_result = service_handler.get_annotation(request_body)
    return annotation_result

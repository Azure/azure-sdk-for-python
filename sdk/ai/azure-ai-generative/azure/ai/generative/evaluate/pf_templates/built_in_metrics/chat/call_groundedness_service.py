from promptflow import tool
from rai_client import RAIServiceHandler


@tool
def call_groundedness_service(request_bodies: list[dict]) -> [dict]:
    service_handler = RAIServiceHandler()
    annotation_results = []
    for request_body in request_bodies:
        try:
            annotation_result = service_handler.get_annotation(request_body)
        except Exception:
            annotation_result = []
        annotation_results += annotation_result
    return annotation_results

from promptflow import tool
from rai_client import RAIServiceHandler

# The inputs section will change based on the
# arguments of the tool function, after you save the code
# Adding type to arguments and return value will help
# the system show the types properly
# Please update the function name/signature per need
@tool
def call_groundedness_service(request_body: dict) -> [dict]:
    service_handler = RAIServiceHandler()
    annotation_results = service_handler.get_annotation(request_body)
    return annotation_results

from promptflow import tool
from mlflow.utils.rest_utils import http_request
import time
from utils import get_cred
from constants import RAIService


def submit_annotation(cred, request_body):
    try:        
        response = http_request(
            host_creds=cred,
            endpoint="/submitannotation",
            method="POST",
            json=request_body,
        )

        if response.status_code != 202:
            print("Fail evaluating '%s' with error message: %s", request_body["UserTextList"], response.text)
            response.raise_for_status()
    except AttributeError as e:
        response = None
        print("Fail evaluating '%s' with error message: %s", request_body["UserTextList"], e)
    if response is not None:
        json_obj = response.json()
    else:
        json_obj = {}
    return json_obj

def check_status(cred, request_id):
        try:
            response = http_request(
                host_creds = cred,
                endpoint="/operations/" + request_id,
                method="GET"
            )
        except AttributeError as e:
            response = None
        return response

def retrieve_annotation_result(cred, submitannotation_response):
        request_id = submitannotation_response["location"].split("/")[-1]
        annotation_result = None
        start = time.time()
        time_elapsed = 0
        request_count = 1
        while True and time_elapsed <= RAIService.TIMEOUT:
            try:
                request_status = check_status(cred, request_id)
            except Exception:
                request_status = None
            if request_status:
                request_status_code = request_status.status_code
                #if request_status_code >= 400:
                    #request_status.raise_for_status()
                if request_status_code == 200:
                    annotation_result = request_status.json()
                    break
            else:
                print("Failed to retrieve the status of RequestID: %s" % request_id)
            request_count += 1
            sleep_time = RAIService.SLEEPTIME ** request_count
            time.sleep(sleep_time)
            time_elapsed = time.time() - start
    
        if time_elapsed > RAIService.TIMEOUT:
            raise TimeoutError("Request times out after %d seconds", RAIService.TIMEOUT)
    
        return annotation_result

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def call_rai_service(request_body: dict) -> dict:
    cred = get_cred()
    submitannotation_response = submit_annotation(cred, request_body)
    annotation_result = retrieve_annotation_result(cred, submitannotation_response)
    return annotation_result
    
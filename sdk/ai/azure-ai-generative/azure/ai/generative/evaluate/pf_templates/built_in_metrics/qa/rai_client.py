from mlflow.utils.rest_utils import http_request
import time
from utils import get_cred
from constants import RAIService
import numpy as np
import json


class RAIServiceHandler:
    def __init__(self):
        self.cred = get_cred()

    def submit_annotation(self, request_body):
        try:
            response = http_request(
                host_creds=self.cred,
                endpoint="/submitannotation",
                method="POST",
                json=request_body,
            )

            if response.status_code != 202:
                print("Fail evaluating '%s' with error message: %s"
                      % (request_body["UserTextList"], response.text))
                response.raise_for_status()
        except AttributeError as e:
            response = None
            print("Fail evaluating '%s' with error message: %s"
                  % (request_body["UserTextList"], e))
        if response is not None:
            json_obj = response.json()
        else:
            json_obj = {}
        return json_obj

    def _check_status(self, request_id):
        print("RAI service: check request_id: %s"
              % request_id)
        try:
            response = http_request(
                host_creds=self.cred,
                endpoint="/operations/" + request_id,
                method="GET"
            )
        except AttributeError:
            response = None
        return response

    def retrieve_annotation_result(self, submitannotation_response):
        request_id = submitannotation_response["location"].split("/")[-1]
        annotation_result = None
        start = time.time()
        time_elapsed = 0
        request_count = 1
        while True and time_elapsed <= RAIService.TIMEOUT:
            try:
                request_status = self._check_status(request_id)
            except Exception:
                request_status = None
            if request_status:
                request_status_code = request_status.status_code
                if request_status_code == 200:
                    annotation_result = request_status.json()
                    break
                if request_status_code >= 400:
                    raw_annotation_result = request_status.json()
                    generic_groundedness_output = {"label": np.nan,
                                                   "reasoning": ""}
                    if isinstance(raw_annotation_result, dict)\
                       and "error" in raw_annotation_result:
                        generic_groundedness_output["reasoning"] =\
                            raw_annotation_result["error"]["message"]
                    annotation_result = [
                        {"generic_groundedness":
                         json.dumps(generic_groundedness_output)}]
                    break
            else:
                print("Failed to retrieve the status of RequestID: %s"
                      % request_id)
            request_count += 1
            sleep_time = RAIService.SLEEPTIME * request_count
            time.sleep(sleep_time)
            time_elapsed = time.time() - start

        if time_elapsed > RAIService.TIMEOUT:
            raise TimeoutError("Request times out after %d seconds"
                               % RAIService.TIMEOUT)

        return annotation_result

    def get_annotation(self, request_body):
        try:
            submitannotation_response = self.submit_annotation(request_body)
            annotation_result = self.retrieve_annotation_result(
                submitannotation_response)
        except Exception:
            annotation_result = None
        return annotation_result

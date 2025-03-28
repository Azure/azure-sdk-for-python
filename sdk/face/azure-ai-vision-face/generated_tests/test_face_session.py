# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import FaceSessionClientTestBase, FaceSessionPreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestFaceSession(FaceSessionClientTestBase):
    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_create_liveness_session(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.create_liveness_session(
            body={
                "livenessOperationMode": "str",
                "authTokenTimeToLiveInSeconds": 0,
                "deviceCorrelationId": "str",
                "deviceCorrelationIdSetInClient": bool,
                "enableSessionImage": bool,
                "livenessModelVersion": "str",
            },
        )

        # please add some check logic here by yourself
        # ...

    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_delete_liveness_session(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.delete_liveness_session(
            session_id="str",
        )

        # please add some check logic here by yourself
        # ...

    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_get_liveness_session_result(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.get_liveness_session_result(
            session_id="str",
        )

        # please add some check logic here by yourself
        # ...

    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_create_liveness_with_verify_session(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.create_liveness_with_verify_session(
            body={
                "livenessOperationMode": "str",
                "verifyImage": "filetype",
                "authTokenTimeToLiveInSeconds": 0,
                "deviceCorrelationId": "str",
                "deviceCorrelationIdSetInClient": bool,
                "enableSessionImage": bool,
                "livenessModelVersion": "str",
                "returnVerifyImageHash": bool,
                "verifyConfidenceThreshold": 0.0,
            },
        )

        # please add some check logic here by yourself
        # ...

    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_delete_liveness_with_verify_session(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.delete_liveness_with_verify_session(
            session_id="str",
        )

        # please add some check logic here by yourself
        # ...

    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_get_liveness_with_verify_session_result(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.get_liveness_with_verify_session_result(
            session_id="str",
        )

        # please add some check logic here by yourself
        # ...

    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_detect_from_session_image(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.detect_from_session_image(
            body={"sessionImageId": "str"},
            session_image_id="str",
        )

        # please add some check logic here by yourself
        # ...

    @FaceSessionPreparer()
    @recorded_by_proxy
    def test_get_session_image(self, facesession_endpoint):
        client = self.create_client(endpoint=facesession_endpoint)
        response = client.get_session_image(
            session_image_id="str",
        )

        # please add some check logic here by yourself
        # ...

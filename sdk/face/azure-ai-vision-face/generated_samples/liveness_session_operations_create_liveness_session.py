# coding=utf-8

from azure.ai.vision.face import FaceSessionClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python liveness_session_operations_create_liveness_session.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.create_liveness_session(
        body={
            "authTokenTimeToLiveInSeconds": 60,
            "deviceCorrelationId": "your_device_correlation_id",
            "deviceCorrelationIdSetInClient": False,
            "livenessOperationMode": "Passive",
        },
    )
    print(response)


# x-ms-original-file: v1.2/LivenessSessionOperations_CreateLivenessSession.json
if __name__ == "__main__":
    main()

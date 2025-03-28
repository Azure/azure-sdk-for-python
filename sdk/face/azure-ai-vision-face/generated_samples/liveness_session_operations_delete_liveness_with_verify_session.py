# coding=utf-8

from azure.ai.vision.face import FaceSessionClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python liveness_session_operations_delete_liveness_with_verify_session.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    client.delete_liveness_with_verify_session(
        session_id="b12e033e-bda7-4b83-a211-e721c661f30e",
    )


# x-ms-original-file: v1.2/LivenessSessionOperations_DeleteLivenessWithVerifySession.json
if __name__ == "__main__":
    main()

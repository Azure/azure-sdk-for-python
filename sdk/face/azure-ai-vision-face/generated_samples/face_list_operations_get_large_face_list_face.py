# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python face_list_operations_get_large_face_list_face.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.large_face_list.get_face(
        large_face_list_id="your_large_face_list_id",
        persisted_face_id="43897a75-8d6f-42cf-885e-74832febb055",
    )
    print(response)


# x-ms-original-file: v1.2/FaceListOperations_GetLargeFaceListFace.json
if __name__ == "__main__":
    main()

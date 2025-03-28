# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python face_list_operations_delete_large_face_list.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    client.large_face_list.delete(
        large_face_list_id="your_large_face_list_id",
    )


# x-ms-original-file: v1.2/FaceListOperations_DeleteLargeFaceList.json
if __name__ == "__main__":
    main()

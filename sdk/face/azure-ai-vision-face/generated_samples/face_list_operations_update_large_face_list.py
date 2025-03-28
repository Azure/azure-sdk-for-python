# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python face_list_operations_update_large_face_list.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    client.large_face_list.update(
        large_face_list_id="your_large_face_list_id",
        body={"name": "your_large_face_list_name", "userData": "your_user_data"},
    )


# x-ms-original-file: v1.2/FaceListOperations_UpdateLargeFaceList.json
if __name__ == "__main__":
    main()

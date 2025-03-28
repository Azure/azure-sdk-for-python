# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python face_list_operations_get_large_face_lists.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.large_face_list.get_large_face_lists()
    print(response)


# x-ms-original-file: v1.2/FaceListOperations_GetLargeFaceLists.json
if __name__ == "__main__":
    main()

# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python person_group_operations_add_large_person_group_person_face_from_stream.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.large_person_group.add_face(
        large_person_group_id="your_large_person_group_id",
        person_id="25985303-c537-4467-b41d-bdb45cd95ca1",
        image_content="<your-image-bytes-here>",
    )
    print(response)


# x-ms-original-file: v1.2/PersonGroupOperations_AddLargePersonGroupPersonFaceFromStream.json
if __name__ == "__main__":
    main()

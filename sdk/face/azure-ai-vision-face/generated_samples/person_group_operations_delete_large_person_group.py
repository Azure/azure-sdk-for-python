# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python person_group_operations_delete_large_person_group.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    client.large_person_group.delete(
        large_person_group_id="your_large_person_group_id",
    )


# x-ms-original-file: v1.2/PersonGroupOperations_DeleteLargePersonGroup.json
if __name__ == "__main__":
    main()

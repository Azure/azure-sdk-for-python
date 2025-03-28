# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python person_group_operations_update_large_person_group_person.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    client.large_person_group.update_person(
        large_person_group_id="your_large_person_group_id",
        person_id="25985303-c537-4467-b41d-bdb45cd95ca1",
        body={"name": "your_large_person_group_person_name", "userData": "your_user_data"},
    )


# x-ms-original-file: v1.2/PersonGroupOperations_UpdateLargePersonGroupPerson.json
if __name__ == "__main__":
    main()

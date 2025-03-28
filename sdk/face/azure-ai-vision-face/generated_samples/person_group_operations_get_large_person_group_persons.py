# coding=utf-8

from azure.ai.vision.face import FaceAdministrationClient

"""
# PREREQUISITES
    pip install azure-ai-vision-face
# USAGE
    python person_group_operations_get_large_person_group_persons.py
"""


def main():
    client = FaceClient(
        endpoint="ENDPOINT",
        credential="CREDENTIAL",
    )

    response = client.large_person_group.get_persons(
        large_person_group_id="your_large_person_group_id",
    )
    print(response)


# x-ms-original-file: v1.2/PersonGroupOperations_GetLargePersonGroupPersons.json
if __name__ == "__main__":
    main()

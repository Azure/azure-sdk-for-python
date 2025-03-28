# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.communication.jobrouter import JobRouterAdministrationClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-communication-jobrouter
# USAGE
    python exception_policies_update_exception_policy.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = JobRouterAdministrationClient(
        endpoint="https://contoso.westus.communications.azure.com",
        credential=DefaultAzureCredential(),
    )

    response = client.upsert_exception_policy(
        exception_policy_id="cf1cda69-6f41-45ac-b252-213293f1b1cb",
        resource={
            "exceptionRules": [
                {
                    "actions": [
                        {"classificationPolicyId": "Main", "kind": "reclassify", "labelsToUpsert": {"escalated": True}}
                    ],
                    "id": "MaxWaitTimeExceeded",
                    "trigger": {"kind": "waitTime", "thresholdSeconds": 20},
                }
            ],
            "name": "Main test",
        },
    )
    print(response)


# x-ms-original-file: 2024-01-18-preview/ExceptionPolicies_UpdateExceptionPolicy.json
if __name__ == "__main__":
    main()

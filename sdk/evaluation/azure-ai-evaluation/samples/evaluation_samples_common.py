# coding: utf-8
# type: ignore

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    These samples demonstrate usage of various classes and methods commonly used in the azure-ai-evaluation library.
    
USAGE:
    python evaluation_samples_common.py
"""


class EvaluationCommonSamples(object):
    def evaluation_common_classes_methods(self):
        # [START create_AOAI_model_config]
        from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration

        model_config = AzureOpenAIModelConfiguration(
            azure_endpoint="https://abcdefghijklmnopqrstuvwxyz.api.cognitive.microsoft.com",
            api_key="my-aoai-api-key",
            api_version="2024-04-01-preview",
            azure_deployment="my-aoai-deployment-name",
        )

        # [END create_AOAI_model_config]

        # [START create_OAI_model_config]
        from azure.ai.evaluation._model_configurations import OpenAIModelConfiguration

        oai_model_config = OpenAIModelConfiguration(
            api_key="my-oai-api-key", base_url="https://api.openai.com/v1", model="gpt-35-turbo"
        )

        # [END create_OAI_model_config]

        # [START create_azure_ai_project_object]
        from azure.ai.evaluation._model_configurations import AzureAIProject

        project = AzureAIProject(
            subscription_id="my-subscription-id",
            resource_group_name="my-resource-group-name",
            project_name="my-project-name",
        )

        # [END create_azure_ai_project_object]


if __name__ == "__main__":
    print("Loading samples in evaluation_samples_common.py")
    sample = EvaluationCommonSamples()
    print("Samples loaded successfully!")
    print("Running samples in evaluation_samples_common.py")
    sample.evaluation_common_classes_methods()
    print("Samples ran successfully!")

# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    Create a Content Understanding skillset with fixed-size character chunks,
    then update it to semantic token chunks and image-description model settings.
    This configuration sample deletes its skillset; it does not run an indexer.

USAGE:
    python sample_skillset_content_understanding.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT, AZURE_SEARCH_API_KEY (an admin key),
    AZURE_AI_SERVICES_ENDPOINT (a Foundry-created AI Services resource supporting
    Content Understanding), AZURE_OPENAI_CHAT_MODEL, and AZURE_OPENAI_CHAT_DEPLOYMENT.
    The chat deployment must exist in the Foundry resource attached to the skillset.
    Grant the Search service's managed identity access to that resource.
    SAMPLE_RUN_TAG optionally supplies a unique resource-name suffix.

    To execute this skill in your own Blob indexer, enable
    IndexingParametersConfiguration.allow_skillset_to_read_file_data so the
    /document/file_data input exists, and map text_sections into your target index.
    Execution incurs Content Understanding/model charges; configuration alone
    does not demonstrate successful enrichment or model availability.
"""

import os

from sample_utils import get_sample_run_tag


def main():
    variables = ("AZURE_AI_SERVICES_ENDPOINT", "AZURE_OPENAI_CHAT_MODEL", "AZURE_OPENAI_CHAT_DEPLOYMENT")
    if not all(os.environ.get(name) for name in variables):
        print("Skipping Content Understanding; set " + ", ".join(variables))
        return

    # [START sample_skillset_content_understanding]
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import ResourceNotFoundError
    from azure.search.documents.indexes import SearchIndexerClient
    from azure.search.documents.indexes.models import (
        AIServicesAccountIdentity,
        ContentUnderstandingSkill,
        ContentUnderstandingSkillChunkingMethod,
        ContentUnderstandingSkillChunkingProperties,
        ContentUnderstandingSkillChunkingUnit,
        InputFieldMappingEntry,
        OutputFieldMappingEntry,
        SearchIndexerSkillset,
    )
    from azure.search.documents.indexes.types import (
        ContentUnderstandingSkill as ContentUnderstandingSkillInput,
        SearchIndexerSkill as SearchIndexerSkillInput,
        SearchIndexerSkillset as SearchIndexerSkillsetInput,
    )

    skillset_name = f"hotels-content-understanding-{get_sample_run_tag()}"
    skill = ContentUnderstandingSkill(
        name="hotel-content",
        context="/document",
        inputs=[InputFieldMappingEntry(name="file_data", source="/document/file_data")],
        outputs=[OutputFieldMappingEntry(name="text_sections", target_name="text_sections")],
        chunking_properties=ContentUnderstandingSkillChunkingProperties(
            method=ContentUnderstandingSkillChunkingMethod.FIXED_SIZE,
            unit=ContentUnderstandingSkillChunkingUnit.CHARACTERS,
            maximum_length=2000,
            overlap_length=200,
        ),
    )
    skillset = SearchIndexerSkillset(
        name=skillset_name,
        skills=[skill],
        cognitive_services_account=AIServicesAccountIdentity(subdomain_url=os.environ["AZURE_AI_SERVICES_ENDPOINT"]),
    )
    with SearchIndexerClient(
        os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"], AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
    ) as indexer_client:
        try:
            indexer_client.create_or_update_skillset(skillset)
            skill.chunking_properties = ContentUnderstandingSkillChunkingProperties(
                method=ContentUnderstandingSkillChunkingMethod.SEMANTIC,
                unit=ContentUnderstandingSkillChunkingUnit.TOKENS,
                maximum_length=500,
                overlap_length=0,
            )
            skill.model_name = os.environ["AZURE_OPENAI_CHAT_MODEL"]
            skill.model_deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
            skillset.skills = [skill]
            updated = indexer_client.create_or_update_skillset(skillset)
            print(f"Configured Content Understanding skillset: {updated.name}")

            typed_skill: ContentUnderstandingSkillInput = {
                "@odata.type": "#Microsoft.Skills.Util.ContentUnderstandingSkill",
                "name": "hotel-content",
                "context": "/document",
                "inputs": [{"name": "file_data", "source": "/document/file_data"}],
                "outputs": [{"name": "text_sections", "targetName": "text_sections"}],
                "chunkingProperties": {
                    "method": "semantic",
                    "unit": "tokens",
                    "maximumLength": 500,
                    "overlapLength": 0,
                },
                "modelName": os.environ["AZURE_OPENAI_CHAT_MODEL"],
                "modelDeployment": os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            }
            skill_input: SearchIndexerSkillInput = typed_skill
            typed_skillset: SearchIndexerSkillsetInput = {
                "name": skillset_name,
                "skills": [skill_input],
                "cognitiveServices": {
                    "@odata.type": "#Microsoft.Azure.Search.AIServicesByIdentity",
                    "subdomainUrl": os.environ["AZURE_AI_SERVICES_ENDPOINT"],
                },
            }
            typed_updated = indexer_client.create_or_update_skillset(typed_skillset)
            print(f"TypedDict skillset: {typed_updated.name}")
        finally:
            try:
                indexer_client.delete_skillset(skillset_name)
            except ResourceNotFoundError:
                pass
    # [END sample_skillset_content_understanding]


if __name__ == "__main__":
    main()

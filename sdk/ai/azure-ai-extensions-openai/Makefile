# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# Extension-owned TypeSpec generation for shared OpenAI/Foundry model contracts.

RESPONSES_TYPESPEC_DIR ?= type_spec/responses
RESPONSES_TEMP_TSP_DIR := $(RESPONSES_TYPESPEC_DIR)/TempTypeSpecFiles
RESPONSES_CONTRACTS_DIR := $(RESPONSES_TEMP_TSP_DIR)/sdk-service-agentserver-contracts
RESPONSES_MODEL_DIR := azure/ai/extensions/openai/responses/_generated/sdk/models

PROJECTS_TYPESPEC_DIR ?= type_spec/projects
PROJECTS_TEMP_TSP_DIR := $(PROJECTS_TYPESPEC_DIR)/TempTypeSpecFiles
PROJECTS_CONTRACTS_DIR := $(PROJECTS_TEMP_TSP_DIR)/sdk-python-js-azure-ai-projects
PROJECTS_MODEL_DIR := azure/ai/extensions/openai/projects/_generated

.PHONY: generate-models generate-responses-models generate-projects-types clean

generate-models: generate-responses-models generate-projects-types

generate-responses-models:
	python _scripts/generate_shared_models.py responses

generate-projects-types:
	python _scripts/generate_shared_models.py projects

clean:
	rm -rf $(RESPONSES_MODEL_DIR) $(PROJECTS_MODEL_DIR)

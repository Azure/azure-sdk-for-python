# coding: utf-8
# type: ignore

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    These samples demonstrate usage of _SafetyEvaluation class with various _SafetyEvaluator instances.
    
USAGE:
    python evaluation_samples_safety_evaluation.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_OPENAI_ENDPOINT
    2) AZURE_OPENAI_API_VERSION
    3) AZURE_OPENAI_DEPLOYMENT
    4) AZURE_SUBSCRIPTION_ID
    5) AZURE_RESOURCE_GROUP_NAME
    6) AZURE_PROJECT_NAME

"""

class EvaluationSafetyEvaluationSamples(object):
    def evaluation_safety_evaluation_classes_methods(self):
        import os
        import asyncio
        from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, _SafetyEvaluator
        from azure.ai.evaluation.simulator import AdversarialScenario
        from azure.identity import DefaultAzureCredential
        # [START default_safety_evaluation]
        def test_target(query: str) -> str:
            return "some response"

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_default = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)
        safety_evaluation_default_results = asyncio.run(safety_evaluation_default(
            target=test_target,
        ))
        # [END default_safety_evaluation]

        # [START default_safety_evaluation_model_target]
        """
        please install the pyrit extra to run this example

        cd azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation
        pip install -e ".[pyrit]"
        """
        model_config = {
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        }

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_default = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)
        safety_evaluation_default_results = asyncio.run(safety_evaluation_default(
            target=model_config,
        ))
        # [END default_safety_evaluation_model_target]

        # [START content_safety_safety_evaluation]

        def test_target(query: str) -> str:
            return "some response"

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_content_safety_single_turn = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)

        safety_evaluation_content_safety_single_turn_results = asyncio.run(safety_evaluation_content_safety_single_turn(
            evaluators=[_SafetyEvaluator.CONTENT_SAFETY],
            evaluation_name="some evaluation",
            target=test_target,
            num_turns=1,
            num_rows=3,
            output_path="evaluation_outputs_safety_single_turn.jsonl",
        ))
        # [END content_safety_safety_evaluation]

        # [START content_safety_multi_turn_safety_evaluation]
        def test_target(query: str) -> str:
            return "some response"
        
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_content_safety_multi_turn = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)

        safety_evaluation_content_safety_multi_turn_results = asyncio.run(safety_evaluation_content_safety_multi_turn(
            evaluators=[_SafetyEvaluator.CONTENT_SAFETY],
            target=test_target,
            num_turns=3,
            num_rows=3,
            output_path="evaluation_outputs_safety_multi_turn.jsonl",
        ))

        # [END content_safety_multi_turn_safety_evaluation]

        # [START content_safety_scenario_safety_evaluation]

        def test_target(query: str) -> str:
            return "some response"

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
    
        credential = DefaultAzureCredential()

        safety_evaluation_content_safety_scenario = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)

        safety_evaluation_content_safety_scenario_results = asyncio.run(safety_evaluation_content_safety_scenario(
            evaluators=[_SafetyEvaluator.CONTENT_SAFETY],
            target=test_target,
            scenario=AdversarialScenario.ADVERSARIAL_SUMMARIZATION,
            num_rows=3,
            output_path="evaluation_outputs_safety_scenario.jsonl",
        ))

        # [END content_safety_scenario_safety_evaluation]

        # [START protected_material_safety_evaluation]
        def test_target(query: str) -> str:
            return "some response"
        
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_protected_material = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)

        safety_evaluation_protected_material_results = asyncio.run(safety_evaluation_protected_material(
            evaluators=[_SafetyEvaluator.PROTECTED_MATERIAL],
            target=test_target,
            num_turns=1,
            num_rows=3,
            output_path="evaluation_outputs_protected_material.jsonl",
        ))

        # [END protected_material_safety_evaluation]

        # [START groundedness_safety_evaluation]
        def test_target(query: str) -> str:
            return "some response"
        
        grounding_data = "some grounding data"
        
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_groundedness = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)
        safety_evaluation_groundedness_results = asyncio.run(safety_evaluation_groundedness(
            evaluators=[_SafetyEvaluator.GROUNDEDNESS],
            target=test_target,
            source_text=grounding_data,
            num_rows=3,
            output_path="evaluation_outputs_groundedness.jsonl",
        ))

        # [END groundedness_safety_evaluation]

        # [START quality_safety_evaluation]
        def test_target(query: str) -> str:
            return "some response"
        
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_quality = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)

        safety_evaluation_quality_results = asyncio.run(safety_evaluation_quality(
            evaluators=[_SafetyEvaluator.RELEVANCE, _SafetyEvaluator.COHERENCE, _SafetyEvaluator.FLUENCY],
            target=test_target,
            num_turns=1,
            num_rows=3,
            output_path="evaluation_outputs_quality.jsonl",
        ))

        # [END quality_safety_evaluation]

        # [START xpia_safety_evaluation]

        def test_target(query: str) -> str:
            return "some response"
        
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_xpia = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)

        safety_evaluation_xpia_results = asyncio.run(safety_evaluation_xpia(
            evaluators=[_SafetyEvaluator.INDIRECT_ATTACK],
            target=test_target,
            num_turns=1,
            num_rows=3,
            output_path="evaluation_outputs_xpia.jsonl",
        ))
        
        # [END xpia_safety_evaluation]

        # [START upia_safety_evaluation]
        def test_target(query: str) -> str:
            return "some response"
        
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_upia = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)
        safety_evaluation_upia_results = asyncio.run(safety_evaluation_upia(
            evaluators=[_SafetyEvaluator.DIRECT_ATTACK],
            target=test_target,
            num_turns=1,
            num_rows=3,
            output_path="evaluation_outputs_upia.jsonl",
        ))
        # [END upia_safety_evaluation]

        # [START eci_safety_evaluation]
        def test_target(query: str) -> str:
            return "some response"
        
        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }

        credential = DefaultAzureCredential()

        safety_evaluation_eci = _SafetyEvaluation(azure_ai_project=azure_ai_project, credential=credential)
        safety_evaluation_eci_results = asyncio.run(safety_evaluation_eci(
            evaluators=[_SafetyEvaluator.ECI],
            target=test_target,
            num_turns=1,
            num_rows=3,
            output_path="evaluation_outputs_eci.jsonl",
        ))
        # [END eci_safety_evaluation]

if __name__ == "__main__":
    print("Loading samples in evaluation_samples_safety_evaluation.py")
    sample = EvaluationSafetyEvaluationSamples()
    print("Samples loaded successfully!")
    print("Running samples in evaluation_samples_safety_evaluation.py")
    sample.evaluation_safety_evaluation_classes_methods()
    print("Samples ran successfully!")

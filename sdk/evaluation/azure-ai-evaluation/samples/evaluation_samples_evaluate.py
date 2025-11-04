# coding: utf-8
# type: ignore

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    These samples demonstrate usage of various classes and methods used to perform evaluation in the azure-ai-evaluation library.

USAGE:
    python evaluation_samples_evaluate.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_OPENAI_ENDPOINT
    2) AZURE_OPENAI_KEY
    3) AZURE_OPENAI_DEPLOYMENT
    4) AZURE_SUBSCRIPTION_ID
    5) AZURE_RESOURCE_GROUP_NAME
    6) AZURE_PROJECT_NAME

"""


class EvaluationEvaluateSamples(object):
    def evaluation_evaluate_classes_methods(self):
        # [START evaluate_method]
        import os
        from azure.ai.evaluation import evaluate, RelevanceEvaluator, CoherenceEvaluator, IntentResolutionEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        print(os.getcwd())
        path = "./sdk/evaluation/azure-ai-evaluation/samples/data/evaluate_test_data.jsonl"

        evaluate(
            data=path,
            evaluators={
                "coherence": CoherenceEvaluator(model_config=model_config),
                "relevance": RelevanceEvaluator(model_config=model_config),
                "intent_resolution": IntentResolutionEvaluator(model_config=model_config),
            },
            evaluator_config={
                "coherence": {
                    "column_mapping": {
                        "response": "${data.response}",
                        "query": "${data.query}",
                    },
                },
                "relevance": {
                    "column_mapping": {
                        "response": "${data.response}",
                        "context": "${data.context}",
                        "query": "${data.query}",
                    },
                },
            },
            # Example of using tags for tracking and organization
            tags={
                "experiment": "basic_evaluation",
                "model": "gpt-4",
                "dataset": "sample_qa_data",
                "environment": "development",
            },
        )

        # [END evaluate_method]

        # [START bleu_score_evaluator]
        from azure.ai.evaluation import BleuScoreEvaluator

        bleu_evaluator = BleuScoreEvaluator()
        bleu_evaluator(response="Lyon is the capital of France.", ground_truth="Paris is the capital of France.")
        # [END bleu_score_evaluator]

        # [START coherence_evaluator]
        import os
        from azure.ai.evaluation import CoherenceEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }
        coherence_evaluator = CoherenceEvaluator(model_config=model_config)
        coherence_evaluator(query="What is the capital of France?", response="Paris is the capital of France.")
        # [END coherence_evaluator]

        # [START intent_resolution_evaluator]
        import os
        from azure.ai.evaluation import IntentResolutionEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }
        intent_resolution_evaluator = IntentResolutionEvaluator(model_config=model_config)
        intent_resolution_evaluator(
            query="What is the opening hours of the Eiffel Tower?",
            response="Opening hours of the Eiffel Tower are 9:00 AM to 11:00 PM.",
        )
        # [END intent_resolution_evaluator]

        # [START content_safety_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import ContentSafetyEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        chat_eval = ContentSafetyEvaluator(azure_ai_project=azure_ai_project, credential=credential)

        chat_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END content_safety_evaluator]

        # [START hate_unfairness_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import HateUnfairnessEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        hate_unfairness_eval = HateUnfairnessEvaluator(azure_ai_project=azure_ai_project, credential=credential)
        hate_unfairness_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END hate_unfairness_evaluator]

        # [START self_harm_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import SelfHarmEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        self_harm_eval = SelfHarmEvaluator(azure_ai_project=azure_ai_project, credential=credential)
        self_harm_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END self_harm_evaluator]

        # [START sexual_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import SexualEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        sexual_eval = SexualEvaluator(azure_ai_project=azure_ai_project, credential=credential)
        sexual_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END sexual_evaluator]

        # [START violence_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import ViolenceEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        violence_eval = ViolenceEvaluator(azure_ai_project=azure_ai_project, credential=credential)
        violence_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END violence_evaluator]

        # [START f1_score_evaluator]
        from azure.ai.evaluation import F1ScoreEvaluator

        f1_evaluator = F1ScoreEvaluator()
        f1_evaluator(response="Lyon is the capital of France.", ground_truth="Paris is the capital of France.")
        # [END f1_score_evaluator]

        # [START fluency_evaluator]
        import os
        from azure.ai.evaluation import FluencyEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        fluency_evaluator = FluencyEvaluator(model_config=model_config)
        fluency_evaluator(response="Paris is the capital of France.")
        # [END fluency_evaluator]

        # [START gleu_score_evaluator]
        from azure.ai.evaluation import GleuScoreEvaluator

        gleu_evaluator = GleuScoreEvaluator()
        gleu_evaluator(response="Paris is the capital of France.", ground_truth="France's capital is Paris.")
        # [END gleu_score_evaluator]

        # [START groundedness_evaluator]
        import os
        from azure.ai.evaluation import GroundednessEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        groundedness_evaluator = GroundednessEvaluator(model_config=model_config)
        groundedness_evaluator(
            response="Paris is the capital of France.",
            context=(
                "France, a country in Western Europe, is known for its rich history and cultural heritage."
                "The city of Paris, located in the northern part of the country, serves as its capital."
                "Paris is renowned for its art, fashion, and landmarks such as the Eiffel Tower and the Louvre Museum."
            ),
        )
        # [END groundedness_evaluator]

        # [START meteor_score_evaluator]
        from azure.ai.evaluation import MeteorScoreEvaluator

        meteor_evaluator = MeteorScoreEvaluator(alpha=0.8)
        meteor_evaluator(response="Paris is the capital of France.", ground_truth="France's capital is Paris.")
        # [END meteor_score_evaluator]

        # [START protected_material_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import ProtectedMaterialEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        protected_material_eval = ProtectedMaterialEvaluator(azure_ai_project=azure_ai_project, credential=credential)
        protected_material_eval(
            query="Write me a catchy song",
            response=(
                "You are the dancing queen, young and sweet, only seventeen."
                "Dancing queen, feel the beat from the tambourine, oh yeah."
            ),
        )
        # [END protected_material_evaluator]

        # [START qa_evaluator]
        import os
        from azure.ai.evaluation import QAEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        qa_eval = QAEvaluator(model_config=model_config)
        qa_eval(query="This's the color?", response="Black", ground_truth="gray", context="gray")
        # [END qa_evaluator]

        # [START relevance_evaluator]
        import os
        from azure.ai.evaluation import RelevanceEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        relevance_eval = RelevanceEvaluator(model_config=model_config)
        relevance_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
        )
        # [END relevance_evaluator]

        # [START retrieval_evaluator]
        import os
        from azure.ai.evaluation import RetrievalEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        retrieval_eval = RetrievalEvaluator(model_config=model_config)
        conversation = {
            "messages": [
                {
                    "content": "What is the capital of France?`''\"</>{}{{]",
                    "role": "user",
                    "context": "Customer wants to know the capital of France",
                },
                {"content": "Paris", "role": "assistant", "context": "Paris is the capital of France"},
                {
                    "content": "What is the capital of Hawaii?",
                    "role": "user",
                    "context": "Customer wants to know the capital of Hawaii",
                },
                {"content": "Honolulu", "role": "assistant", "context": "Honolulu is the capital of Hawaii"},
            ],
            "context": "Global context",
        }
        retrieval_eval(conversation=conversation)
        # [END retrieval_evaluator]

        # [START rouge_score_evaluator]
        from azure.ai.evaluation import RougeScoreEvaluator, RougeType

        rouge_evaluator = RougeScoreEvaluator(rouge_type=RougeType.ROUGE_4)
        rouge_evaluator(response="Paris is the capital of France.", ground_truth="France's capital is Paris.")
        # [END rouge_score_evaluator]

        # [START similarity_evaluator]
        import os
        from azure.ai.evaluation import SimilarityEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        similarity_eval = SimilarityEvaluator(model_config=model_config)
        similarity_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital.",
        )
        # [END similarity_evaluator]

        # [START task_adherence_evaluator]
        import os
        from azure.ai.evaluation import TaskAdherenceEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        task_adherence_evaluator = TaskAdherenceEvaluator(model_config=model_config)

        query = [
            {"role": "system", "content": "You are a helpful customer service agent."},
            {"role": "user", "content": [{"type": "text", "text": "What is the status of my order #123?"}]},
        ]

        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call": {
                            "id": "tool_001",
                            "type": "function",
                            "function": {"name": "get_order", "arguments": {"order_id": "123"}},
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "tool_001",
                "content": [
                    {"type": "tool_result", "tool_result": '{ "order": { "id": "123", "status": "shipped" } }'}
                ],
            },
            {"role": "assistant", "content": [{"type": "text", "text": "Your order #123 has been shipped."}]},
        ]

        tool_definitions = [
            {
                "name": "get_order",
                "description": "Get order details.",
                "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}},
            }
        ]

        task_adherence_evaluator(query=query, response=response, tool_definitions=tool_definitions)
        # [END task_adherence_evaluator]

        # [START task_completion_evaluator]
        import os
        from azure.ai.evaluation._evaluators._task_completion import _TaskCompletionEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        task_completion_evaluator = _TaskCompletionEvaluator(model_config=model_config)

        query = [
            {"role": "system", "content": "You are a travel booking assistant. Help users find and book flights."},
            {
                "role": "user",
                "content": [{"type": "text", "text": "I need to book a flight from London to Paris for tomorrow"}],
            },
        ]

        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call": {
                            "id": "search_001",
                            "type": "function",
                            "function": {
                                "name": "search_flights",
                                "arguments": {
                                    "origin": "London",
                                    "destination": "Paris",
                                    "departure_date": "2025-08-13",
                                },
                            },
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "search_001",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": '{"flights": [{"flight_id": "BA309", "price": "£89", "departure": "10:30", "arrival": "13:45"}, {"flight_id": "AF1234", "price": "£95", "departure": "14:20", "arrival": "17:35"}]}',
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I found 2 flights from London to Paris for tomorrow:\n\n1. BA309 departing 10:30, arriving 13:45 - £89\n2. AF1234 departing 14:20, arriving 17:35 - £95\n\nWould you like me to book one of these flights for you?",
                    }
                ],
            },
        ]

        tool_definitions = [
            {
                "name": "search_flights",
                "description": "Search for available flights between two cities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {"type": "string", "description": "Departure city"},
                        "destination": {"type": "string", "description": "Arrival city"},
                        "departure_date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
                    },
                },
            }
        ]

        task_completion_evaluator(query=query, response=response, tool_definitions=tool_definitions)
        # [END task_completion_evaluator]

        # [START indirect_attack_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import IndirectAttackEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        indirect_attack_eval = IndirectAttackEvaluator(azure_ai_project=azure_ai_project, credential=credential)
        indirect_attack_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END indirect_attack_evaluator]

        # [START groundedness_pro_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import GroundednessProEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        groundedness_pro_eval = GroundednessProEvaluator(azure_ai_project=azure_ai_project, credential=credential)
        groundedness_pro_eval(
            query="What shape has 4 equilateral sides?",
            response="Rhombus",
            context="Rhombus is a shape with 4 equilateral sides.",
        )
        # [END groundedness_pro_evaluator]

        # [START tool_call_accuracy_evaluator]
        import os
        from azure.ai.evaluation import ToolCallAccuracyEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        tool_call_accuracy_evaluator = ToolCallAccuracyEvaluator(model_config=model_config)
        tool_call_accuracy_evaluator(
            query="How is the weather in New York?",
            response="The weather in New York is sunny.",
            tool_calls={
                "type": "tool_call",
                "tool_call": {
                    "id": "call_eYtq7fMyHxDWIgeG2s26h0lJ",
                    "type": "function",
                    "function": {"name": "fetch_weather", "arguments": {"location": "New York"}},
                },
            },
            tool_definitions={
                "id": "fetch_weather",
                "name": "fetch_weather",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "The location to fetch weather for."}},
                },
            },
        )
        # [END tool_call_accuracy_evaluator]

        # [START tool_success_evaluator]
        import os
        import json
        from azure.ai.evaluation._evaluators._tool_success import _ToolSuccessEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        tool_success_evaluator = _ToolSuccessEvaluator(model_config=model_config)
        tool_success_evaluator(
            response=json.loads(
                """[{"createdAt": "2025-08-16T08:39:47Z", "run_id": "run_id22", "role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_id557", "name": "get_date", "arguments": {}}]}, {"createdAt": "2025-08-16T08:39:49Z", "run_id": "run_id22", "tool_call_id": "call_id557", "role": "tool", "content": [{"type": "tool_result", "tool_result": {"date_and_time": "2019-09-07 23:59:59"}}]}, {"createdAt": "2025-08-16T08:39:51Z", "run_id": "run_id22", "role": "assistant", "content": [{"type": "tool_call", "tool_call_id": "call_Run1", "name": "get_spending_by_day", "arguments": {"start_date": "2019-10-01", "end_date": "2019-10-31"}}]}, {"createdAt": "2025-08-16T08:39:53Z", "run_id": "run_id22", "tool_call_id": "call_Run1", "role": "tool", "content": [{"type": "tool_result", "tool_result": {"spending": {}}}]}, {"createdAt": "2025-08-16T08:39:54Z", "run_id": "run_id22", "role": "assistant", "content": [{"type": "text", "text": "There are no spending records for October."}]}]"""
            ),
            tool_definitions=json.loads(
                """[{"name": "get_categories", "type": "function", "description": "Retrieve of a spending line id from your spending records."}]"""
            ),
        )

        tool_success_evaluator(
            response="the agent called get_categories and the call returned the value Electronics",
            tool_definitions="We have a tool named get_categories that takes the spending line id as a input and outputs the category of this spending line",
        )
        # [END tool_success_evaluator]

        # [START tool_output_utilization]
        import os
        from azure.ai.evaluation import _ToolOutputUtilizationEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        tool_output_utilization_evaluator = _ToolOutputUtilizationEvaluator(model_config=model_config)
        query = [
            {"role": "system", "content": "You are a customer service assistant helping with order inquiries."},
            {"role": "user", "content": [{"type": "text", "text": "What's the status of order #12345?"}]},
        ]

        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_456",
                        "name": "get_order_status",
                        "arguments": {"order_id": "12345"},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_456",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {
                            "order_id": "12345",
                            "status": "shipped",
                            "tracking_number": "1Z999AA1234567890",
                            "estimated_delivery": "2024-10-03",
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Your order #12345 has been shipped! The tracking number is 1Z999AA1234567890 and it's estimated to arrive on October 3rd, 2024.",
                    }
                ],
            },
        ]

        tool_definitions = [
            {
                "name": "get_order_status",
                "type": "function",
                "description": "Retrieves current status and details for an order",
                "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}},
            }
        ]

        tool_output_utilization_evaluator(query=query, response=response, tool_definitions=tool_definitions)
        # [END tool_output_utilization]

        # [START task_navigation_efficiency_evaluator]
        from azure.ai.evaluation._evaluators._task_navigation_efficiency import (
            _TaskNavigationEfficiencyEvaluator,
            _TaskNavigationEfficiencyMatchingMode,
        )

        task_navigation_efficiency_evaluator = _TaskNavigationEfficiencyEvaluator(
            matching_mode=_TaskNavigationEfficiencyMatchingMode.EXACT_MATCH
        )

        response = [
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_2", "name": "analyze", "arguments": {}}],
            },
            {
                "role": "assistant",
                "content": [{"type": "tool_call", "tool_call_id": "call_3", "name": "report", "arguments": {}}],
            },
        ]
        ground_truth = ["search", "analyze", "report"]

        task_navigation_efficiency_evaluator(response=response, ground_truth=ground_truth)

        # Also supports tuple format with parameters for exact parameter matching
        response_with_params = [
            {
                "role": "assistant",
                "content": [
                    {"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {"query": "test"}}
                ],
            },
        ]
        ground_truth_with_params = (["search"], {"search": {"query": "test"}})

        task_navigation_efficiency_evaluator(response=response_with_params, ground_truth=ground_truth_with_params)
        # [END task_navigation_efficiency_evaluator]

        # [START document_retrieval_evaluator]
        from azure.ai.evaluation import DocumentRetrievalEvaluator

        retrieval_ground_truth = [
            {"document_id": "1", "query_relevance_label": 4},
            {"document_id": "2", "query_relevance_label": 2},
            {"document_id": "3", "query_relevance_label": 3},
            {"document_id": "4", "query_relevance_label": 1},
            {"document_id": "5", "query_relevance_label": 0},
        ]

        retrieved_documents = [
            {"document_id": "2", "relevance_score": 45.1},
            {"document_id": "6", "relevance_score": 35.8},
            {"document_id": "3", "relevance_score": 29.2},
            {"document_id": "5", "relevance_score": 25.4},
            {"document_id": "7", "relevance_score": 18.8},
        ]

        document_retrieval_evaluator = DocumentRetrievalEvaluator()
        document_retrieval_evaluator(
            retrieval_ground_truth=retrieval_ground_truth, retrieved_documents=retrieved_documents
        )
        # [END document_retrieval_evaluator]

        # [START evaluate_with_tags_examples]
        evaluate(
            data=path,
            evaluators={"coherence": CoherenceEvaluator(model_config=model_config)},
            evaluator_config={
                "coherence": {
                    "column_mapping": {
                        "response": "${data.response}",
                        "query": "${data.query}",
                    },
                },
            },
            azure_ai_project=azure_ai_project,
            tags={
                "experiment_name": "coherence_baseline",
                "model_version": "gpt-4-0613",
                "dataset_version": "v1.2",
                "researcher": "data_science_team",
                "cost_center": "ai_research",
            },
        )
        # [END evaluate_with_tags_examples]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    print("Loading samples in evaluation_samples_evaluate.py")
    sample = EvaluationEvaluateSamples()
    print("Samples loaded successfully!")
    print("Running samples in evaluation_samples_evaluate.py")
    sample.evaluation_evaluate_classes_methods()
    print("Samples ran successfully!")

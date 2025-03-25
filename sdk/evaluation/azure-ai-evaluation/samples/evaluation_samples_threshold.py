# coding: utf-8
# type: ignore

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
DESCRIPTION:
    These samples demonstrate usage of various classes and methods used to perform evaluation with thresholds in the azure-ai-evaluation library.
    
USAGE:
    python evaluation_samples_threshold.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_OPENAI_ENDPOINT
    2) AZURE_OPENAI_KEY
    3) AZURE_OPENAI_DEPLOYMENT
    4) AZURE_SUBSCRIPTION_ID
    5) AZURE_RESOURCE_GROUP_NAME
    6) AZURE_PROJECT_NAME

"""
class EvaluationThresholdSamples(object):
    def evaluation_classes_methods_with_thresholds(self):
        # [START threshold_evaluate_method]
        import os
        from azure.ai.evaluation import evaluate, RelevanceEvaluator, CoherenceEvaluator

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
                "coherence": CoherenceEvaluator(model_config=model_config, threshold=2),
                "relevance": RelevanceEvaluator(model_config=model_config, threshold=4),
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
        )

        # [END threshold_evaluate_method]

        # [START threshold_bleu_score_evaluator]
        from azure.ai.evaluation import BleuScoreEvaluator

        bleu_evaluator = BleuScoreEvaluator(threshold=0.3)
        bleu_score = bleu_evaluator(response="Lyon is the capital of France.", ground_truth="Paris is the capital of France.")
        print(f"BLEU Score: {bleu_score['bleu_score']}, Result: {bleu_score['bleu_result']}, Threshold: {bleu_score['bleu_threshold']}")
        # [END threshold_bleu_score_evaluator]

        # [START threshold_coherence_evaluator]
        import os
        from azure.ai.evaluation import CoherenceEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }
        coherence_evaluator = CoherenceEvaluator(model_config=model_config, threshold=2)
        coherence_evaluator(query="What is the capital of France?", response="Paris is the capital of France.")
        print(f"Coherence Score: {coherence_evaluator['coherence']}, Result: {coherence_evaluator['coherence_result']}, Threshold: {coherence_evaluator['coherence_threshold']}")
        # [END coherence_evaluator]

        # [START threshold_content_safety_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import ContentSafetyEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        chat_eval = ContentSafetyEvaluator(azure_ai_project=azure_ai_project, credential=credential, threshold=3)

        chat_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END threshold_content_safety_evaluator]

        # [START threshold_hate_unfairness_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import HateUnfairnessEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        hate_unfairness_eval = HateUnfairnessEvaluator(azure_ai_project=azure_ai_project, credential=credential, threshold=1)
        hate_unfairness_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END threshold_hate_unfairness_evaluator]

        # [START threshold_self_harm_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import SelfHarmEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        self_harm_eval = SelfHarmEvaluator(azure_ai_project=azure_ai_project, credential=credential, threshold=4)
        self_harm_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END threshold_self_harm_evaluator]

        # [START threshold_sexual_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import SexualEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        sexual_eval = SexualEvaluator(azure_ai_project=azure_ai_project, credential=credential, threshold=1)
        sexual_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END threshold_sexual_evaluator]

        # [START threshold_violence_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import ViolenceEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        violence_eval = ViolenceEvaluator(azure_ai_project=azure_ai_project, credential=credential, threshold=1)
        violence_eval(
            query="What is the capital of France?",
            response="Paris",
        )
        # [END threshold_violence_evaluator]

        # [START threshold_f1_score_evaluator]
        from azure.ai.evaluation import F1ScoreEvaluator

        f1_evaluator = F1ScoreEvaluator(threshold=0.6)
        f1_evaluator(response="Lyon is the capital of France.", ground_truth="Paris is the capital of France.")
        # [END threshold_f1_score_evaluator]

        # [START threshold_fluency_evaluator]
        import os
        from azure.ai.evaluation import FluencyEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        fluency_evaluator = FluencyEvaluator(model_config=model_config, threshold=0.4)
        fluency_evaluator(response="Paris is the capital of France.")
        # [END threshold_fluency_evaluator]

        # [START threshold_gleu_score_evaluator]
        from azure.ai.evaluation import GleuScoreEvaluator

        gleu_evaluator = GleuScoreEvaluator(threshold=0.2)
        gleu_evaluator(response="Paris is the capital of France.", ground_truth="France's capital is Paris.")
        # [END threshold_gleu_score_evaluator]

        # [START threshold_groundedness_evaluator]
        import os
        from azure.ai.evaluation import GroundednessEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        groundedness_evaluator = GroundednessEvaluator(model_config=model_config, threshold=2)
        groundedness_evaluator(
            response="Paris is the capital of France.",
            context=(
                "France, a country in Western Europe, is known for its rich history and cultural heritage."
                "The city of Paris, located in the northern part of the country, serves as its capital."
                "Paris is renowned for its art, fashion, and landmarks such as the Eiffel Tower and the Louvre Museum."
            ),
        )
        # [END threshold_groundedness_evaluator]

        # [START threshold_meteor_score_evaluator]
        from azure.ai.evaluation import MeteorScoreEvaluator

        meteor_evaluator = MeteorScoreEvaluator(alpha=0.8, threshold=0.3)
        meteor_evaluator(response="Paris is the capital of France.", ground_truth="France's capital is Paris.")
        # [END threshold_meteor_score_evaluator]

        # [START threshold_qa_evaluator]
        import os
        from azure.ai.evaluation import QAEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        qa_eval = QAEvaluator(
            model_config=model_config, 
            groundedness_threshold=2,
            relevance_threshold=2,
            coherence_threshold=2,
            fluency_threshold=2,
            similarity_threshold=2,
            f1_score_threshold=0.5
        )
        qa_eval(query="This's the color?", response="Black", ground_truth="gray", context="gray")
        # [END threshold_qa_evaluator]

        # [START threshold_relevance_evaluator]
        import os
        from azure.ai.evaluation import RelevanceEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        relevance_eval = RelevanceEvaluator(model_config=model_config, threshold=2)
        relevance_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
        )
        # [END threshold_relevance_evaluator]

        # [START threshold_retrieval_evaluator]
        import os
        from azure.ai.evaluation import RetrievalEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        retrieval_eval = RetrievalEvaluator(model_config=model_config, threshold=2)
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
        # [END threshold_retrieval_evaluator]

        # [START threshold_rouge_score_evaluator]
        from azure.ai.evaluation import RougeScoreEvaluator, RougeType

        rouge_evaluator = RougeScoreEvaluator(
            rouge_type=RougeType.ROUGE_4, 
            precision_threshold=0.5,
            recall_threshold=0.5,
            f1_score_threshold=0.5
        )
        rouge_evaluator(response="Paris is the capital of France.", ground_truth="France's capital is Paris.")
        # [END threshold_rouge_score_evaluator]

        # [START threshold_similarity_evaluator]
        import os
        from azure.ai.evaluation import SimilarityEvaluator

        model_config = {
            "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_KEY"),
            "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        }

        similarity_eval = SimilarityEvaluator(model_config=model_config, threshold=3)
        similarity_eval(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital.",
        )
        # [END threshold_similarity_evaluator]

        # [START threshold_groundedness_pro_evaluator]
        import os
        from azure.identity import DefaultAzureCredential
        from azure.ai.evaluation import GroundednessProEvaluator

        azure_ai_project = {
            "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
            "project_name": os.environ.get("AZURE_PROJECT_NAME"),
        }
        credential = DefaultAzureCredential()

        groundedness_pro_eval = GroundednessProEvaluator(azure_ai_project=azure_ai_project, credential=credential, threshold=2)
        groundedness_pro_eval(
            query="What shape has 4 equilateral sides?",
            response="Rhombus",
            context="Rhombus is a shape with 4 equilateral sides.",
        )
        # [END threshold_groundedness_pro_evaluator]


if __name__ == "__main__":
    print("Loading samples in evaluation_samples_evaluate.py")
    sample = EvaluationThresholdSamples()
    print("Samples loaded successfully!")
    print("Running samples in evaluation_samples_evaluate.py")
    sample.evaluation_classes_methods_with_thresholds()
    print("Samples ran successfully!")
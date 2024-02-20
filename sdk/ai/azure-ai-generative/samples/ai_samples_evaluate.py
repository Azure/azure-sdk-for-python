# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_evaluate.py

DESCRIPTION:
    These samples demonstrate evaluation api usage.

USAGE:
    python ml_samples_evaluate.py

"""


class AIEvaluateSamples(object):
    def ai_evaluate_qa(self):

        # [START evaluate_task_type_qa]
        import os
        from azure.ai.generative.evaluate import evaluate
        from azure.ai.resources.client import AIClient
        from azure.identity import DefaultAzureCredential

        data_location = "<path_to_data_in_jsonl_format>"

        def sample_chat(question):
            # Logic for chat application ....
            return question

        client = AIClient.from_config(DefaultAzureCredential())
        result = evaluate(
            evaluation_name="my-evaluation",
            target=sample_chat, # Optional if provided evaluate will call target with data provided
            data=data_location,
            task_type="qa",
            data_mapping={
                "questions": "question",
                "contexts": "context",
                "y_pred": "answer",
                "y_test": "truth"
            },
            model_config={
                "api_version": "2023-05-15",
                "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "api_type": "azure",
                "api_key": os.getenv("AZURE_OPENAI_KEY"),
                "deployment_id": os.getenv("AZURE_OPENAI_EVALUATION_DEPLOYMENT")
            },
            tracking_uri=client.tracking_uri,
        )

        # [END evaluate_task_type_qa]

        # [START evaluate_custom_metrics]
        import os
        from azure.ai.generative import evaluate
        from azure.ai.resources.client import AIClient
        from azure.identity import DefaultAzureCredential
        from azure.ai.generative.evaluate.metrics import PromptMetric

        data_location = "<path_to_data_in_jsonl_format>"

        def sample_chat(question):
            # Logic for chat application ....
            return question

        # Code Metric
        def answer_length(*, data, **kwargs):
            return {
                "answer_length": len(data.get("answer")),
            }

        # Prompt Metric
        custom_relevance = PromptMetric(
            name="custom_relevance",
            prompt="""
        System:
        You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a question-answering task. Your job is to compute an accurate evaluation score using the provided evaluation metric.

        User:
        Relevance measures how well the answer addresses the main aspects of the question, based on the context. Consider whether all and only the important aspects are contained in the answer when evaluating relevance. Given the context and question, score the relevance of the answer between one to five stars using the following rating scale:
        One star: the answer completely lacks relevance
        Two stars: the answer mostly lacks relevance
        Three stars: the answer is partially relevant
        Four stars: the answer is mostly relevant
        Five stars: the answer has perfect relevance

        This rating value should always be an integer between 1 and 5. So the rating produced should be 1 or 2 or 3 or 4 or 5.

        context: Marie Curie was a Polish-born physicist and chemist who pioneered research on radioactivity and was the first woman to win a Nobel Prize.
        question: What field did Marie Curie excel in?
        answer: Marie Curie was a renowned painter who focused mainly on impressionist styles and techniques.
        stars: 1

        context: The Beatles were an English rock band formed in Liverpool in 1960, and they are widely regarded as the most influential music band in history.
        question: Where were The Beatles formed?
        answer: The band The Beatles began their journey in London, England, and they changed the history of music.
        stars: 2

        context: {{context}}
        question: {{question}}
        answer: {{answer}}
        stars:

        Your response must include following fields and should be in json format:
        score: Number of stars based on definition above
        reason: Reason why the score was given
                    """
        )

        client = AIClient.from_config(DefaultAzureCredential())
        result = evaluate(
            evaluation_name="my-evaluation",
            target=sample_chat,  # Optional if provided evaluate will call target with data provided
            data=data_location,
            task_type="qa",
            metrics_list=["gpt_groundedness", answer_length, custom_relevance],
            data_mapping={
                "questions": "question",
                "contexts": "context",
                "y_pred": "answer",
                "y_test": "truth"
            },
            model_config={
                "api_version": "2023-05-15",
                "api_base": os.getenv("OPENAI_API_BASE"),
                "api_type": "azure",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "deployment_id": os.getenv("AZURE_OPENAI_EVALUATION_DEPLOYMENT")
            },
            tracking_uri=client.tracking_uri,
        )

        # [END evaluate_custom_metrics]


if __name__ == "__main__":
    sample = AIEvaluateSamples()
    sample.ai_evaluate_qa()

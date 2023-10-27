# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Question-Answer Data Generator."""

try:
    import asyncio
    import os
    import json
    import time
    from enum import Enum
    from functools import lru_cache
    from typing import Dict, List, Tuple, Any, Union
    import openai
    from collections import defaultdict
    from azure.ai.resources.entities import BaseConnection
    from azure.identity import DefaultAzureCredential
    from azure.ai.generative._telemetry import ActivityType, monitor_with_activity, OpsLogger
    from azure.core.tracing.decorator import distributed_trace
except ImportError as e:
    print("In order to use qa, please install the 'qa_generation' extra of azure-ai-generative")
    raise e


_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger

_DEFAULT_AOAI_VERSION = "2023-07-01-preview"
_MAX_RETRIES = 7
_RETRY_ERRORS = (
    openai.error.ServiceUnavailableError,
    openai.error.APIError,
    openai.error.RateLimitError,
    openai.error.APIConnectionError,
    openai.error.Timeout,
)


def _completion_with_retries(*args, **kwargs):
    n = 1
    while True:
        try:
            response = openai.ChatCompletion.create(*args, **kwargs)
        except _RETRY_ERRORS as e:
            if n > _MAX_RETRIES:
                raise
            secs = 2 ** n
            logger.warning(f"Retrying after {secs}s. API call failed due to {e.__class__.__name__}: {e}")
            time.sleep(secs)
            n += 1
            continue
        return response


async def _completion_with_retries_async(*args, **kwargs):
    n = 1
    while True:
        try:
            response = await openai.ChatCompletion.acreate(*args, **kwargs)
        except _RETRY_ERRORS as e:
            if n > _MAX_RETRIES:
                raise
            secs = 2 ** n
            logger.warning(f"Retrying after {secs}s. API call failed due to {e.__class__.__name__}: {e}")
            await asyncio.sleep(secs)
            n += 1
            continue
        return response


class QAType(str, Enum):
    """QAType defines different types of QAs that can be generated."""

    SHORT_ANSWER = "SHORT_ANSWER"
    """Short answer QAs have answers that are only a few words long. These words are generally relevant details from text like dates, names, statistics, etc."""
    LONG_ANSWER = "LONG_ANSWER"
    """Long answer QAs have answers that are one or more sentences long. ex. Questions where answer is a definition: What is a {topic_from_text}?"""
    BOOLEAN = "BOOLEAN"
    """Boolean QAs have answers that are either True or False."""
    SUMMARY = "SUMMARY"
    """Summary QAs have questions that ask to write a summary for text's title in a limited number of words. It generates just one QA."""
    CONVERSATION = "CONVERSATION"
    """Conversation QAs have questions that might reference words or ideas from previous QAs. ex. If previous conversation was about
    some topicX from text, next question might reference it without using its name: How does *it* compare to topicY?"""

class QADataGenerator:
    """Class for generating Question-Answer data from text."""
    _PARSING_ERR_UNEQUAL_QA = "Parsing error: Unequal question answer count"
    _PARSING_ERR_UNEQUAL_Q_AFTER_MOD = "Parsing error: Unequal question count after modification"
    _PARSING_ERR_FIRST_LINE = "Parsing error: First line must be a question"

    def __init__(self, model_config: Dict, connection: BaseConnection = None, **kwargs: Any):
        """Initialize QADataGenerator using Azure OpenAI details."""
        if connection:
            if connection.type != "azure_open_ai":
                raise TypeError("QADataGenerator only supports AzureOpenAI connections")
            metadata = connection.metadata
            api_type = metadata.get("apiType") or metadata.get("ApiType", "azure")
            api_type = api_type.lower()
            if api_type == "azure_ad":
                default_credential = DefaultAzureCredential()
                api_key = default_credential.get_token("https://cognitiveservices.azure.com/.default").token
            elif connection.credentials.type.lower() == "api_key":
                api_key = connection.credentials.key
            else:
                raise ValueError(f"Unknown auth type '{connection.credentials.type}' for connection '{connection.name}'")
            self._chat_completion_params = dict(
                api_type=api_type,
                api_version=metadata.get("apiVersion") or metadata.get("ApiVersion", _DEFAULT_AOAI_VERSION),
                api_base=connection.target,
                api_key=api_key,
                deployment_id=model_config["deployment"],
                model=model_config["model"],
                max_tokens=model_config.get("max_tokens", 2000),
                temperature=0.0,  # don't need creativity
            )
        else:
            self._chat_completion_params = dict(
                api_type=model_config.get("api_type", "azure"),
                api_version=model_config.get("api_version", _DEFAULT_AOAI_VERSION),
                api_base=model_config["api_base"],
                api_key=model_config["api_key"],
                deployment_id=model_config["deployment"],
                model=model_config["model"],
                max_tokens=model_config.get("max_tokens", 2000),
                temperature=0.0,  # don't need creativity
            )
        ops_logger.update_info(kwargs)

    def _validate(self, qa_type: QAType, num_questions: int):
        if qa_type == QAType.SUMMARY and num_questions is not None:
            raise ValueError("num_questions unsupported for Summary QAType")
        if qa_type != QAType.SUMMARY and num_questions <= 0:
            raise ValueError("num_questions must be an integer greater than zero")

    def _get_messages_for_qa_type(self, qa_type: QAType, text: str, num_questions: int) -> List:
        logger.debug(f"Getting prompt messages for {qa_type} QA type")
        template_filename = {
            QAType.SHORT_ANSWER: "prompt_qa_short_answer.txt",
            QAType.LONG_ANSWER: "prompt_qa_long_answer.txt",
            QAType.BOOLEAN: "prompt_qa_boolean.txt",
            QAType.SUMMARY: "prompt_qa_summary.txt",
            QAType.CONVERSATION: "prompt_qa_conversation.txt"
        }
        filename = template_filename[qa_type]
        messages = self._get_messages_from_file(filename)
        input_variables = {"text": text}
        if qa_type == QAType.SUMMARY:
            input_variables["num_words"] = 100
        else:
            input_variables["num_questions"] = num_questions
        messages[-1]["content"] = messages[-1]["content"].format(**input_variables)
        return messages

    def _get_messages_for_modify_conversation(self, questions: List[str]) -> List:
        messages = self._get_messages_from_file("prompt_qa_conversation_modify.txt")
        questions_str = "\n".join([f"[Q]: {q}" for q in questions])
        messages[-1]["content"] = messages[-1]["content"].format(questions=questions_str)
        return messages

    def _get_messages_from_file(self, filename: str) -> List:
        template = self._get_template(filename)
        content_list = [content.strip() for content in template.split("<|separator|>")]
        messages = [
            {"role": "system", "content": content_list[0]},  # system instructions
            {"role": "user", "content": content_list[1]},  # few-shot input
            {"role": "assistant", "content": content_list[2]},  # few-shot output
            {"role": "user", "content": content_list[3]},  # input template
        ]
        return messages

    @lru_cache
    def _get_template(self, filename) -> str:
        logger.debug(f"Getting prompt template from {filename} file")
        filepath = os.path.join(_TEMPLATES_DIR, filename)
        with open(filepath) as f:
            template = f.read()
        return template

    def _parse_qa_from_response(self, response_text: str) -> Tuple[List[str], List[str]]:
        response_text = response_text
        q_prefix, a_prefix = "[Q]: ", "[A]: "
        last_updated = None
        questions, answers = [], []
        for line in response_text.split("\n"):
            if line.startswith(q_prefix):
                questions.append(line[len(q_prefix):])
                last_updated = "Q"
            elif line.startswith(a_prefix):
                answers.append(line[len(a_prefix):])
                last_updated = "A"
            else:  # Q or A spread across multiple lines
                assert last_updated is not None, self._PARSING_ERR_FIRST_LINE
                if last_updated == "Q":
                    questions[-1] += "\n" + line
                else:
                    answers[-1] += "\n" + line
        return questions, answers

    def _merge_token_usage(self, token_usage: Dict, token_usage2: Dict) -> Dict:
        return {name: count + token_usage[name] for name, count in token_usage2.items()}

    def _modify_conversation_questions(self, questions) -> Tuple[List[str], Dict]:
        response = _completion_with_retries(
            messages=self._get_messages_for_modify_conversation(questions),
            **self._chat_completion_params,
        )
        modified_questions, _ = self._parse_qa_from_response(response["choices"][0].message.content)
        assert len(modified_questions) == len(questions), self._PARSING_ERR_UNEQUAL_Q_AFTER_MOD
        return modified_questions, response["usage"]

    @distributed_trace
    @monitor_with_activity(logger, "QADataGenerator.Export", ActivityType.INTERNALCALL)
    def export_to_file(self, output_path: str, qa_type: QAType, results: Union[List, List[List]]):
        """
            Writes results from QA gen to a jsonl file for Promptflow batch run
            results is either a list of questions and answers or list of list of questions and answers grouped by their chunk
                e.g. [("How are you?", "I am good.")]    or [ [("How are you?", "I am good.")], [("What can I do?", "Tell me a joke.")]
        """
        data_dict = defaultdict(list)
        
        if not isinstance(results[0], List):
            results = [results]
        
        for qs_and_as in results:
            chat_history = []
            for question, answer in qs_and_as: 
                if qa_type == QAType.CONVERSATION:
                    # Chat History columns:
                    data_dict["chat_history"].append(json.dumps(chat_history))
                    data_dict["chat_input"].append(question)
                    chat_history.append({"inputs": {"chat_input": question}, "outputs": {"chat_output": answer}})
                else:
                    # QnA columns:
                    data_dict["question"].append(question)   

                data_dict["ground_truth"].append(answer)  # Consider generated answer as the ground truth

        # export to jsonl file
        try:
            import pandas as pd
        except ImportError as e:
            print("In order to write qa data to file, please install pandas")
            raise e

        data_df = pd.DataFrame(data_dict, columns=list(data_dict.keys()))
        data_df.to_json(output_path, lines=True, orient="records")

    @distributed_trace
    @monitor_with_activity(logger, "QADataGenerator.Generate", ActivityType.INTERNALCALL)
    def generate(self, text: str, qa_type: QAType, num_questions: int = None) -> Dict:
        self._validate(qa_type, num_questions)
        response = _completion_with_retries(
            messages=self._get_messages_for_qa_type(qa_type, text, num_questions),
            **self._chat_completion_params,
        )
        questions, answers = self._parse_qa_from_response(response["choices"][0].message.content)
        assert len(questions) == len(answers), self._PARSING_ERR_UNEQUAL_QA
        token_usage = response["usage"]
        if qa_type == QAType.CONVERSATION:
            questions, token_usage2 = self._modify_conversation_questions(questions)
            token_usage = self._merge_token_usage(token_usage, token_usage2)
        return {
            "question_answers": list(zip(questions, answers)),
            "token_usage": token_usage,
        }

    async def _modify_conversation_questions_async(self, questions) -> Tuple[List[str], Dict]:
        response = await _completion_with_retries_async(
            messages=self._get_messages_for_modify_conversation(questions),
            **self._chat_completion_params,
        )
        modified_questions, _ = self._parse_qa_from_response(response["choices"][0].message.content)
        assert len(modified_questions) == len(questions), self._PARSING_ERR_UNEQUAL_Q_AFTER_MOD
        return modified_questions, response["usage"]

    @distributed_trace
    @monitor_with_activity(logger, "QADataGenerator.GenerateAsync", ActivityType.INTERNALCALL)
    async def generate_async(self, text: str, qa_type: QAType, num_questions: int = None) -> Dict:
        self._validate(qa_type, num_questions)
        response = await _completion_with_retries_async(
            messages=self._get_messages_for_qa_type(qa_type, text, num_questions),
            **self._chat_completion_params,
        )
        questions, answers = self._parse_qa_from_response(response["choices"][0].message.content)
        assert len(questions) == len(answers), self._PARSING_ERR_UNEQUAL_QA
        token_usage = response["usage"]
        if qa_type == QAType.CONVERSATION:
            questions, token_usage2 = await self._modify_conversation_questions_async(questions)
            token_usage = self._merge_token_usage(token_usage, token_usage2) 
        return {
            "question_answers": list(zip(questions, answers)),
            "token_usage": token_usage,
        }

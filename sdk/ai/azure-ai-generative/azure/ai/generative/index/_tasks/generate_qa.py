# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import time
import traceback
from argparse import ArgumentParser
from logging import Logger
from typing import Dict, Union

import openai
import pandas as pd
from azureml.core import Run
from azure.ai.generative.index.data_generation.qa import QADataGenerator, GenerationResult, QAType
from azure.ai.resources._index._utils.connections import (get_connection_by_id_v2,
                                           get_connection_credential,
                                           connection_to_credential)
from azure.ai.generative.index._utils.logging import (enable_appinsights_logging,
                                       enable_stdout_logging, get_logger,
                                       track_activity, _logger_factory)

LLM_MAX_RETRIES = 15
logger = get_logger("generate_qa")


def get_model_config(llm_config: Dict[str, Union[str, int]], openai_api_type: str, openai_api_version: str, activity_logger: Logger):
    """Get model_config from llm_config. llm_config format is used in Baker pipelines.
    model_config format is accepted by `azure.ai.resources._index._models.init_llm()`."""
    model_config = llm_config.copy()
    model_config['kind'] = model_config['type']
    del model_config['type']
    model_config['model'] = model_config['model_name']
    del model_config['model_name']
    model_config['deployment'] = model_config['deployment_name']
    del model_config['deployment_name']
    if model_config["kind"] == "azure_open_ai":
        model_config["kind"] = "open_ai"
        model_config["api_type"] = openai_api_type
        model_config["api_version"] = openai_api_version
    elif model_config["kind"] == "open_ai":
        model_config["kind"] = "open_ai"
        model_config["api_type"] = openai_api_type
    else:
        raise NotImplementedError(f"LLM type '{model_config['kind']}' not supported!")

    connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_AOAI")
    if connection_id:
        connection_config = {
            "connection_type": "workspace_connection",
            "connection": {"id": connection_id},
        }
        connection = get_connection_by_id_v2(connection_id)
        # Only change base, version, and type in AOAI case, otherwise trust input
        if connection.get('properties', {}).get("category", None) == "AzureOpenAI":
            model_config["api_base"] = connection['properties'].get('target', {})  # type: ignore[assignment]
            model_config["api_type"] = connection['properties'].get('metadata', {}).get('apiType', "azure")
            model_config["api_version"] = connection['properties'].get('metadata', {}).get('apiVersion', "2023-03-15-preview")
        credential = connection_to_credential(connection)
    else:
        connection_config = {"connection_type": "workspace_keyvault"}
        credential = get_connection_credential(connection_config)

    model_config["max_retries"] = LLM_MAX_RETRIES
    activity_logger.info(f"model_config: {model_config}")  # log it before adding PII "key"
    model_config["key"] = credential.key

    # Set openai variables in openai module instead of setting env vars ex. OPENAI_API_KEY.
    # These are used by `langchain.llms.AzureOpenAI`.
    openai.api_type = model_config["api_type"]
    openai.api_key = model_config["key"]

    # Only add base and version if using AOAI
    if model_config["api_type"] == "azure":
        # openai.api_base is replaced by openai.base_url in openai 1.x
        if hasattr(openai, "api_base"):
            openai.api_base = model_config["api_base"]
        else:
            openai.base_url = model_config["api_base"]
        openai.api_version = model_config["api_version"]
    return model_config


def main(parser_args, run, logger: Logger, activity_logger: Logger):
    start_time = time.time()
    activity_logger.info(f"llm_config: {parser_args.llm_config}")
    llm_config = json.loads(parser_args.llm_config)
    model_config = get_model_config(llm_config, parser_args.openai_api_type, parser_args.openai_api_version,
                                    activity_logger)
    qa_generator = QADataGenerator(model_config=model_config,
                                   logger=logger,
                                   activity_logger=activity_logger)
    qa_types = [QAType(qa_type) for qa_type in parser_args.qa_types.split(",")]
    try:
        result = qa_generator.generate(input_dir=parser_args.input_data,
                                       total_questions=parser_args.dataset_size,
                                       chunk_batch_size=parser_args.chunk_batch_size,
                                       qa_types=qa_types)
    except (Exception, KeyboardInterrupt) as e:
        result: GenerationResult = getattr(e, "generation_result", None)  # type: ignore[no-redef]
        if result is None or result.data_df.empty:
            raise
        activity_logger.warn(f"Ignoring exception in QADataGenerator since partial result is available. Exception: {traceback.format_exc()}")

    # log run metrics
    generated_size = len(result.data_df.index)
    time_taken = time.time() - start_time
    activity_logger.info(f"Generated dataset with {generated_size} QAs in {time_taken} secs")
    run.log("generated_dataset_size", generated_size)
    run.log("time_taken_secs", time_taken)
    run.log("total_tokens", result.token_usage.get("total_tokens", 0))
    run.log("prompt_tokens", result.token_usage.get("prompt_tokens", 0))
    run.log("completion_tokens", result.token_usage.get("completion_tokens", 0))
    run.log("model_name", model_config["model"])

    # save qa data to file
    output_dir = parser_args.output_data
    os.makedirs(output_dir, exist_ok=True)
    if parser_args.output_format == "csv":
        qa_data_file = os.path.join(output_dir, "QAGenerationData.csv")
        result.data_df.to_csv(qa_data_file, index=False)
    else:
        qa_data_file = os.path.join(output_dir, "QAGenerationData.jsonl")
        result.data_df.to_json(qa_data_file, lines=True, orient="records")


def main_wrapper(parser_args, run, logger):
    with track_activity(logger, "generate_qa") as activity_logger:
        try:
            main(parser_args, run, logger, activity_logger)
        except Exception:
            activity_logger.error(f"generate_qa failed with exception: {traceback.format_exc()}")  # activity_logger doesn't log traceback
            raise


if __name__ == '__main__':
    enable_stdout_logging()
    enable_appinsights_logging()

    parser = ArgumentParser()
    parser.add_argument("--input-data", type=str, required=True, dest="input_data")
    parser.add_argument("--output-data", type=str, required=True, dest="output_data")
    parser.add_argument("--dataset_size", type=int, required=False, default=100)
    parser.add_argument("--chunk_batch_size", type=int, required=False, default=10)
    parser.add_argument("--output_format", type=str, required=False, default="json")
    parser.add_argument("--llm_config", type=str, default='{"type": "azure_open_ai","model_name": "gpt-35-turbo", "deployment_name": "gpt-35-turbo", "temperature": 0, "max_tokens": 3000}')
    parser.add_argument("--qa_types", type=str, default='SHORT_ANSWER,LONG_ANSWER,BOOLEAN,SUMMARY')
    parser.add_argument("--openai_api_version", type=str)
    parser.add_argument("--openai_api_type", type=str)
    parser_args = parser.parse_args()

    run = Run.get_context()
    try:
        main_wrapper(parser_args, run, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)  # wait for appinsights to send telemetry
    run.complete()

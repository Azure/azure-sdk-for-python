# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""File for the deployment validation."""

import argparse
import json
import os
import time
import traceback
from logging import Logger
from pathlib import Path
from typing import Optional, Tuple

import openai
import requests
from azure.ai.ml.identity import AzureMLOnBehalfOfCredential
from azure.core.exceptions import HttpResponseError
from azure.identity import AzureCliCredential, ManagedIdentityCredential
from azureml.core import Run, Workspace
from azureml.core.run import _OfflineRun
from azure.ai.ml.entities._indexes.utils.connections import (
    get_connection_by_id_v2,
    get_connection_credential,
    get_id_from_connection,
    get_metadata_from_connection,
    get_target_from_connection,
    workspace_connection_to_credential,
)
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    track_activity,
)
from azure.ai.ml.entities._indexes.utils.tokens import tiktoken_cache_dir
from packaging import version

openai_v1plus = version.parse(openai.version.VERSION) >= version.parse("1.0.0")

logger = get_logger("validate_deployments")


MAX_RETRIES = 3
SLEEP_DURATION = 2


def get_cognitive_services_client(subscription_id: str):
    """Get cognitive services client."""
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

    client_id = os.environ.get("DEFAULT_IDENTITY_CLIENT_ID", None)
    if os.environ.get("OBO_ENDPOINT"):
        print("Using User Identity for authentication")
        credential = AzureMLOnBehalfOfCredential()
        os.environ["MSI_ENDPOINT"] = os.environ.get("OBO_ENDPOINT", "")
    elif client_id:
        print("Using Managed Identity for authentication")
        credential = ManagedIdentityCredential(client_id=client_id)
    else:
        print("Using Azure CLI for authentication")
        credential = AzureCliCredential()
    return CognitiveServicesManagementClient(credential=credential, subscription_id=subscription_id)


def validate_and_create_default_aoai_resource(
    subscription_id: str, resource_group: str, model_params: dict, activity_logger: Logger
):
    """Validate default AOAI deployments and attempt creation if does not exist."""
    resource_group_name = model_params.get("resource_group", resource_group)
    deployment_name = model_params["deployment_id"]

    account_name = model_params["default_aoai_name"]
    activity_logger.info(
        f"[Validate Deployments]: Searching {deployment_name} deployment under account {account_name}"
        + f"in resource group {resource_group_name}."
    )
    client = get_cognitive_services_client(subscription_id)
    try:
        response = client.deployments.get(
            resource_group_name=resource_group_name,
            account_name=account_name,
            deployment_name=deployment_name,
        )
    except HttpResponseError as ex:
        activity_logger.warning(f"[Validate Deployments]: Got error response: '{ex.reason}'.")

        connection_id_embedding = model_params["connection"]
        connection = get_connection_by_id_v2(connection_id_embedding)
        hub_workspace_details = split_details(get_metadata_from_connection(connection)["ProxyResourceId"], start=1)
        proxy_subscription_id = hub_workspace_details["subscriptions"]
        proxy_resource_group = hub_workspace_details.get("resourceGroups", hub_workspace_details["resourcegroups"])
        proxy_workspace_name = hub_workspace_details["workspaces"]

        # Hack: Use proxy url template to access AOAI deployment with specific app version
        # 1st and 3rd line cannot be f-string otherwise it will fail the check.
        proxy_url = (
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            + f"/providers/Microsoft.MachineLearningServices/workspaces/{proxy_workspace_name}"
            + "/endpoints/Azure.OpenAI/deployments/{deploymentName}"
        )
        api_version = "2023-10-01"

        activity_logger.info(f"Try to use proxy url '{proxy_url}' with app version '{api_version}'.")

        # create new client with proxy subscription id
        client = get_cognitive_services_client(proxy_subscription_id)

        client.deployments.get.metadata["url"] = proxy_url
        response = client.deployments.get(
            resource_group_name=proxy_resource_group,
            account_name=account_name,
            deployment_name=deployment_name,
            api_version=api_version,
        )

    response_status = str.lower(response.properties.provisioning_state)
    if response_status != "succeeded":
        # Log this because we need to find out what the possible states are
        print(f"Deployment is not yet in status 'succeeded'. Current status is: {response_status}")
    if response_status in ["failed", "deleting"]:
        # Do not allow polling to continue if deployment state is failed or deleting
        activity_logger.info(
            f"ValidationFailed: Deployment {model_params['deployment_id']} for model "
            + f"{model_params['model_name']} is in failed or deleting state. Please resubmit job with a "
            + "successful deployment."
        )
        raise Exception(
            f"Deployment {model_params['deployment_id']} for model {model_params['model_name']} is in failed or deleting state. Please resubmit job with a successful deployment."
        )
    completion_succeeded = response_status == "succeeded"
    if completion_succeeded:
        activity_logger.info(
            f"[Validate Deployments]: Default AOAI resource deployment {model_params['deployment_id']} for "
            + f"model {model_params['model_name']} is in 'succeeded' status"
        )
    return completion_succeeded


def check_deployment_status(model_params: dict, model_type, activity_logger: Logger):
    """
    Check deployment status of the model deployment in AOAI.

    Attempt to create the deployment, but if the deployment_name does not match what customer wanted,
        throw Exception.
    """
    if not model_params:
        return True

    openai.api_type = model_params["openai_api_type"]
    openai.api_version = model_params["openai_api_version"]
    openai.api_key = model_params["openai_api_key"]

    # api_base is changed to base_url in openai 1.x
    if openai_v1plus:
        openai.base_url = model_params["openai_api_base"]
    else:
        openai.api_base = model_params["openai_api_base"]

    if model_params["openai_api_type"].lower() != "azure" or not model_params["deployment_id"]:
        # If OAI (not-azure), just pass through validation
        activity_logger.info(
            "[Validate Deployments]: Not an Azure Open AI resource - pass through validation.",
            extra={
                "properties": {
                    "openai_api_type": model_params["openai_api_type"].lower(),
                    "deployment_id": model_params["deployment_id"],
                }
            },
        )
        return True

    ws, _ = get_workspace_and_run()

    if (
        "default_aoai_name" in model_params
        and split_details(model_params["connection"], start=1)["connections"] == "Default_AzureOpenAI"
    ):
        # Special control plane validation for default AOAI connection
        activity_logger.info(
            "[Validate Deployments]: Default AOAI resource detected. Performing control plane validations now...",
            extra={
                "properties": {
                    "model_type": model_type,
                    "model_name": model_params["model_name"],
                    "deployment_name": model_params["deployment_id"],
                }
            },
        )
        return validate_and_create_default_aoai_resource(
            ws.subscription_id, ws.resource_group, model_params, activity_logger
        )
    else:
        activity_logger.info(
            "[Validate Deployments]: Non-default AOAI resource detected. Performing data plane validations now...",
            extra={
                "properties": {
                    "model_type": model_type,
                    "model_name": model_params["model_name"],
                    "deployment_name": model_params["deployment_id"],
                }
            },
        )
        # Data plane validation for non-default AOAI resource
        if model_type == "llm":
            from langchain.chains import LLMChain
            from langchain.chat_models import AzureChatOpenAI
            from langchain.llms import AzureOpenAI
            from langchain.prompts import PromptTemplate

            if "gpt-" in model_params["model_name"]:
                model_kwargs = {
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                }
                llm = AzureChatOpenAI(
                    azure_deployment=model_params["deployment_id"],
                    model_name=model_params["model_name"],
                    model_kwargs=model_kwargs,
                    openai_api_key=model_params["openai_api_key"],
                    azure_endpoint=model_params["openai_api_base"],
                    openai_api_version=model_params["openai_api_version"],
                    openai_api_type=model_params["openai_api_type"],
                )
            else:
                llm = AzureOpenAI(
                    deployment_name=model_params["deployment_id"],
                    model_name=model_params["model_name"],
                    openai_api_key=model_params["openai_api_key"],
                )
            try:
                template = (
                    "Answer the following question" + "\n\nContext:\n{context}\n\nQuestion: {question}\n\n Answer:"
                )
                prompt = PromptTemplate(template=template, input_variables=["context", "question"])
                llm_chain = LLMChain(prompt=prompt, llm=llm)
                llm_chain.run(
                    {
                        "context": "Say Yes if you received the the question",
                        "question": "Did you receive the question?",
                    }
                )
            except Exception as ex:
                _throw_aoai_deployment_not_found_error(ex, model_params["deployment_id"], activity_logger)
                raise
        elif model_type == "embedding":
            if openai_v1plus:
                from langchain.embeddings import AzureOpenAIEmbeddings

                embeddings = AzureOpenAIEmbeddings(
                    azure_deployment=model_params["deployment_id"],
                    azure_endpoint=model_params["openai_api_base"],
                    model=model_params["model_name"],
                    openai_api_key=model_params["openai_api_key"],
                    openai_api_version=model_params["openai_api_version"],
                    openai_api_type=model_params["openai_api_type"],
                )
            else:
                from langchain.embeddings import OpenAIEmbeddings

                embeddings = OpenAIEmbeddings(
                    deployment_name=model_params["deployment_id"],
                    model=model_params["model_name"],
                    openai_api_key=model_params["openai_api_key"],
                    openai_api_type=model_params["openai_api_type"],
                )
            try:
                with tiktoken_cache_dir():
                    embeddings.embed_query("Embed this query to test if deployment exists")
            except Exception as ex:
                _throw_aoai_deployment_not_found_error(ex, model_params["deployment_id"], activity_logger)
                raise
        return True


def _throw_aoai_deployment_not_found_error(ex: Exception, deployment_name: str, activity_logger: Logger) -> None:
    """Throw ValueError if AOAI deployment is not found."""
    # from openai 1.0 and above, InvalidRequestError is replaced by BadRequestError
    if (
        (hasattr(openai, "BadRequestError") and isinstance(ex, openai.BadRequestError))
        or (hasattr(openai, "InvalidRequestError") and isinstance(ex, openai.InvalidRequestError))
    ) and ("Resource not found" in str(ex) or "The API deployment for this resource does not exist" in str(ex)):
        activity_logger.info(
            f"ValidationFailed: Deployment validation failed due to the following exception: {traceback.format_exc()}."
        )
        raise ValueError(f"Model deployment '{deployment_name}' is not found.") from ex


def poll_on_deployment(completion_params, embedding_params, activity_logger: Logger):
    """Poll on check_deployment_status for completion and embeddings model deployments."""
    activity_logger.info("[Validate Deployments]: Starting to poll on deployment status validation.")
    start_time = time.time()
    while True:
        if check_deployment_status(completion_params, "llm", activity_logger) and check_deployment_status(
            embedding_params, "embedding", activity_logger
        ):
            break
        if time.time() - start_time > 1800:
            raise TimeoutError("Deployment validation timed out after 1800 seconds.")
        time.sleep(10)


def split_details(details, start):
    """Split details of embeddings model uri."""
    details = details.split("/")
    dets = {}
    for i in range(start, len(details), 2):
        dets[details[i]] = details[i + 1]
    return dets


def get_workspace_and_run() -> Tuple[Workspace, Run]:
    """get_workspace_and_run."""
    run = Run.get_context()
    workspace = Workspace.from_config() if isinstance(run, _OfflineRun) else run.experiment.workspace
    return workspace, run


def is_default_connection(connection) -> bool:
    """Check if connection retrieved is a default AOAI connection."""
    return connection.name == "Default_AzureOpenAI"


def validate_aoai_deployments(
    activity_logger: Logger,
    embeddings_model: Optional[str] = None,
    embeddings_connection_id: Optional[str] = None,
    llm_config: Optional[dict] = None,
    llm_connection_id: Optional[str] = None,
    output: Optional[str] = None,
):
    """Poll or create deployments in AOAI."""
    completion_params = {}
    embedding_params = {}

    print(f"Using llm_config: {json.dumps(llm_config, indent=2)}")

    activity_logger.info(
        "[Validate Deployments]: Received and parsed arguments for validating deployments in RAG. "
        + " Starting validation now..."
    )

    if llm_config and llm_connection_id:
        llm_connection = get_connection_by_id_v2(llm_connection_id)
        credential = workspace_connection_to_credential(llm_connection)
        if hasattr(credential, "key"):
            completion_params["deployment_id"] = llm_config["deployment_name"]
            print(f"Completion model deployment name: {completion_params['deployment_id']}")
            completion_params["model_name"] = llm_config["model_name"]
            print(f"Completion model name: {completion_params['model_name']}")
            completion_params["openai_api_key"] = credential.key
            completion_params["openai_api_base"] = get_target_from_connection(llm_connection)
            connection_metadata = get_metadata_from_connection(llm_connection)
            completion_params["openai_api_type"] = connection_metadata.get(
                "apiType", connection_metadata.get("ApiType", "azure")
            )
            completion_params["openai_api_version"] = connection_metadata.get(
                "apiVersion",
                connection_metadata.get("ApiVersion", "2023-03-15-preview"),
            )
            completion_params["connection"] = get_id_from_connection(llm_connection)
            # Name is currently the only distinguishing factor between default and non-default
            # Default connection is the only one which can perform control plane operations,
            # as AI Studio does not allow selecting of ResourceID in their UI yet.
            if is_default_connection(llm_connection):
                activity_logger.info(
                    "[Validate Deployments]: Completion model using Default AOAI connection, parsing ResourceId"
                )
                cog_workspace_details = split_details(connection_metadata["ResourceId"], start=1)
                completion_params["default_aoai_name"] = cog_workspace_details["accounts"]
                completion_params["resource_group"] = cog_workspace_details["resourceGroups"]
        if not completion_params:
            activity_logger.info("ValidationFailed: Completion model LLM connection was unable to pull information")
            raise Exception("Completion model LLM connection was unable to pull information")
        activity_logger.info(
            "[Validate Deployments]: Completion workspace connection retrieved and params populated successfully...",
            extra={
                "properties": {
                    "connection": get_id_from_connection(llm_connection),
                    "openai_api_type": completion_params["openai_api_type"],
                    "model_name": completion_params["model_name"],
                    "deployment_name": completion_params["deployment_id"],
                    "is_default_aoai": "default_aoai_name" in completion_params,
                }
            },
        )

    # Embedding connection will not be passed in for Existing ACS scenario
    if embeddings_model and embeddings_connection_id:
        embeddings_connection = get_connection_by_id_v2(embeddings_connection_id)
        credential = workspace_connection_to_credential(embeddings_connection)
        _, details = embeddings_model.split("://")
        if hasattr(credential, "key"):
            embedding_params["deployment_id"] = split_details(details, start=0)["deployment"]
            print(f"Embedding deployment name: {embedding_params['deployment_id']}")
            embedding_params["model_name"] = split_details(details, start=0)["model"]
            print(f"Embedding model name: {embedding_params['model_name']}")
            embedding_params["openai_api_key"] = credential.key
            embedding_params["openai_api_base"] = get_target_from_connection(embeddings_connection)
            connection_metadata = get_metadata_from_connection(embeddings_connection)
            embedding_params["openai_api_type"] = connection_metadata.get(
                "apiType", connection_metadata.get("ApiType", "azure")
            )
            embedding_params["openai_api_version"] = connection_metadata.get(
                "apiVersion",
                connection_metadata.get("ApiVersion", "2023-03-15-preview"),
            )
            embedding_params["connection"] = get_id_from_connection(embeddings_connection)
            if is_default_connection(embeddings_connection):
                activity_logger.info(
                    "[Validate Deployments]: Embedding model using Default AOAI connection, parsing ResourceId"
                )
                cog_workspace_details = split_details(connection_metadata["ResourceId"], start=1)
                embedding_params["default_aoai_name"] = cog_workspace_details["accounts"]
                embedding_params["resource_group"] = cog_workspace_details["resourceGroups"]
            print("Using workspace connection key for OpenAI embeddings")
        if not embedding_params:
            activity_logger.info("ValidationFailed: Embedding model connection was unable to pull information")
            raise Exception("Embeddings connection was unable to pull information")
        activity_logger.info(
            "[Validate Deployments]: Embedding workspace connection retrieved and params populated successfully...",
            extra={
                "properties": {
                    "connection": get_id_from_connection(embeddings_connection),
                    "openai_api_type": embedding_params["openai_api_type"],
                    "model_name": embedding_params["model_name"],
                    "deployment_name": embedding_params["deployment_id"],
                    "is_default_aoai": "default_aoai_name" in embedding_params,
                }
            },
        )

    poll_on_deployment(completion_params, embedding_params, activity_logger)
    # Dummy output to allow step ordering
    if output:
        with Path(output).open("w") as f:
            json.dump({"deployment_validation_success": "true"}, f)

    activity_logger.info("[Validate Deployments]: Success! AOAI deployments have been validated.")


def get_openai_model(model: str, key: str, activity_logger: Logger):
    """Get model info from OpenAI."""
    endpoint = f"https://api.openai.com/v1/models/{model}"
    headers = {"Authorization": f"Bearer {key}"}
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
    except Exception as e:
        activity_logger.exception(
            f"Unable to get model information from OpenAI for model {model}: Exception Type: {type(e)}"
        )
        raise


def validate_openai_deployments(
    activity_logger: Logger,
    embeddings_model: Optional[str] = None,
    embeddings_connection_id: Optional[str] = None,
    llm_config: Optional[dict] = None,
    llm_connection_id: Optional[str] = None,
    output: Optional[str] = None,
):
    """Call OpenAI to check for model ids."""
    if llm_config and llm_connection_id:
        print(f"Using llm_config: {json.dumps(llm_config, indent=2)}")

        llm_connection = get_connection_by_id_v2(llm_connection_id)
        credential = workspace_connection_to_credential(llm_connection)
        model = llm_config["model_name"]
        print(f"Completion model name: {model}")
        get_openai_model(model, credential.key, activity_logger)

    if embeddings_model and embeddings_connection_id:
        embeddings_connection = get_connection_by_id_v2(embeddings_connection_id)
        credential = workspace_connection_to_credential(embeddings_connection)
        _, details = embeddings_model.split("://")
        model = split_details(details, start=0)["model"]
        print(f"Embeddings model name: {model}")
        get_openai_model(model, credential.key, activity_logger)

    # dummy output to allow step ordering
    if output:
        with Path(output).open("w") as f:
            json.dump({"deployment_validation_success": "true"}, f)

    activity_logger.info("[Validate Deployments]: Success! OpenAI deployments have been validated.")


def validate_acs(
    activity_logger: Logger,
    acs_config: Optional[dict],
    acs_connection_id: Optional[str],
) -> None:
    """Call ACS Client to check for valid Azure Search instance."""
    activity_logger.info("[Validate Deployments]: Validating ACS config and connection for ACS index creation...")

    #  Do not validate ACS if inputs are not sufficient
    if not acs_config or not acs_config.get("index_name") or not acs_connection_id:
        activity_logger.info("[Validate Deployments]: ACS config or ACS connection id is missing. Skip ACS validation.")
        return

    import re

    from azure.search.documents.indexes import SearchIndexClient

    index_name = acs_config.get("index_name")
    if (
        index_name is None
        or index_name == ""
        or index_name.startswith("-")
        or index_name.endswith("-")
        or (not re.search("^[a-z0-9-_]+$", index_name))
        or len(index_name) > 128
    ):
        error_msg = (
            "Invalid acs index name provided. Index name must only contain"
            "lowercase letters, digits, dashes and underscores and "
            "cannot start or end with dashes and is limited to 128 characters."
        )
        activity_logger.error(f"[Validate Deployments]: {error_msg}.")
        raise ValueError(error_msg)

    acs_connection = get_connection_by_id_v2(acs_connection_id)
    acs_config["endpoint"] = get_target_from_connection(acs_connection)
    acs_metadata = get_metadata_from_connection(acs_connection)
    acs_config["api_version"] = acs_metadata.get("apiVersion", "2023-07-01-preview")

    connection_args = {
        "connection_type": "workspace_connection",
        "connection": {"id": get_id_from_connection(acs_connection)},
    }

    credential = get_connection_credential(connection_args)

    statistics = {}
    index_names = []
    for retry_counter in range(MAX_RETRIES):
        try:
            index_client = SearchIndexClient(
                endpoint=acs_config["endpoint"],
                credential=credential,
                api_version=acs_config["api_version"],
            )
            index_names = list(index_client.list_index_names())
            statistics = index_client.get_service_statistics()
            activity_logger.info("[Validate Deployments]: Success! ACS instance can be invoked and has been validated.")
            break
        except Exception as ex:
            if retry_counter < MAX_RETRIES:
                activity_logger.info(f"[Validate Deployments]: Failed to validate ACS. Retry after {SLEEP_DURATION} seconds.")
                time.sleep(SLEEP_DURATION)
            else:
                activity_logger.error(
                    f"[Validate Deployments]: Failed to reach ACS. Exception: {traceback.format_exc()}"
                )
                raise ex

    if acs_config["index_name"] in index_names:
        activity_logger.info(
            f"[Validate Deployments]: ACS index with name '{acs_config['index_name']}' already exists in the ACS account."
        )
    elif statistics["counters"]["index_counter"]["usage"] < statistics["counters"]["index_counter"]["quota"]:
        activity_logger.info(
            f"[Validate Deployments]: ACS index with name '{acs_config['index_name']}' does not exist in the ACS account. ACS account has enough quota to create the index."
        )
    else:
        raise ValueError(
            f"[Validate Deployments]: ACS index with name '{acs_config['index_name']}' does not exists in the ACS account. ACS account has reached the quota limit for the number of indexes."
        )


def validate_deployments(
    embeddings_model: str,
    activity_logger: Logger,
    embeddings_connection_id: Optional[str] = None,
    llm_config: Optional[dict] = None,
    llm_connection_id: Optional[str] = None,
    output: Optional[str] = None,
) -> None:
    """Validate deployments."""
    if (embeddings_model and embeddings_model.startswith("azure_open_ai")) or (
        llm_config and llm_config.get("type") == "azure_open_ai"
    ):
        completion_to_check = "Completion model" if (llm_config and llm_config.get("type") == "azure_open_ai") else ""
        embeddings_to_check = "Embeddings model" if embeddings_model.startswith("azure_open_ai") else ""
        use_and = " and " if embeddings_to_check != "" and completion_to_check != "" else ""
        activity_logger.info(
            f"[Validate Deployments]: Validating {completion_to_check}{use_and}{embeddings_to_check} using AOAI"
        )
        validate_aoai_deployments(
            activity_logger,
            embeddings_model,
            embeddings_connection_id=embeddings_connection_id,
            llm_config=llm_config,
            llm_connection_id=llm_connection_id,
            output=output,
        )

    if (embeddings_model and embeddings_model.startswith("open_ai")) or (
        llm_config and llm_config.get("type") == "open_ai"
    ):
        completion_to_check = "Completion model" if (llm_config and llm_config.get("type") == "open_ai") else ""
        embeddings_to_check = "Embeddings model" if embeddings_model.startswith("open_ai") else ""
        use_and = " and " if embeddings_to_check != "" and len(completion_to_check) else ""
        activity_logger.info(
            f"[Validate Deployments]: Validating {completion_to_check}{use_and}{embeddings_to_check} using OpenAI"
        )
        validate_openai_deployments(
            activity_logger,
            embeddings_model,
            embeddings_connection_id,
            llm_config=llm_config,
            llm_connection_id=llm_connection_id,
            output=output,
        )


def main(args, activity_logger: Logger):
    """
    Main method.

        Validate the deployments for the given embeddings and/or LLM models.
        Validate the ACS index creation if index_config and index_connection_id are provided.

    """
    if args.embeddings_connection_id is None:
        args.embeddings_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_AOAI_EMBEDDING", None)
        activity_logger.info(
            f"Get default embeddings connection id from environment variable: {args.embeddings_connection_id}"
        )

    if args.llm_connection_id is None:
        args.embeddings_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_AOAI_COMPLETION", None)
        activity_logger.info(f"Get default LLM connection id from environment variable: {args.llm_connection_id}")

    if args.index_connection_id is None:
        args.index_connection_id = os.environ.get("AZUREML_WORKSPACE_CONNECTION_ID_ACS", None)
        activity_logger.info(f"Get default ACS connection id from environment variable: {args.index_connection_id}")

    # Validate Embedding and/or LLM deployments
    validate_deployments(
        embeddings_model=args.embeddings_model,
        activity_logger=activity_logger,
        embeddings_connection_id=args.embeddings_connection_id,
        llm_config=json.loads(args.llm_config),
        llm_connection_id=args.llm_connection_id,
        output=args.output_data,
    )
    activity_logger.info("[Validate Deployments]: Validating deployments completed successfully.")

    # Validate ACS index creation
    # TODO: Using index type to determine if ACS index creation is needed. This is a temporary solution.
    validate_acs(
        activity_logger,
        acs_config=json.loads(args.index_config) if args.index_config else None,
        acs_connection_id=args.index_connection_id,
    )
    activity_logger.info("[Validate Deployments]: Validating ACS completed successfully.")


def main_wrapper(args, logger):
    """Wrap around main function with activity_logger."""
    with track_activity(
        logger,
        "validate_deployments",
        custom_dimensions={
            "llm_config": args.llm_config,
            "embeddings_model": args.embeddings_model,
            "index_config": args.index_config,
        },
    ) as activity_logger:
        try:
            main(args, activity_logger)
        except Exception:
            # activity_logger doesn't log traceback
            activity_logger.error(
                f"[Validate Deployments]: validate_deployments failed with exception: {traceback.format_exc()}"
            )
            raise


if __name__ == "__main__":
    enable_stdout_logging()
    enable_appinsights_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("--embeddings_model", type=str, required=False)
    parser.add_argument("--embeddings_connection_id", type=str, required=False)
    parser.add_argument(
        "--llm_config",
        type=str,
        default='{"type": "azure_open_ai","model_name": "gpt-35-turbo", "deployment_name": '
        + '"gpt-35-turbo", "temperature": 0, "max_tokens": 2000}',
    )
    parser.add_argument("--llm_connection_id", type=str, required=False)
    parser.add_argument("--index_config", type=str, required=False)
    parser.add_argument("--index_connection_id", type=str, required=False)
    parser.add_argument("--output_data", type=str)  # Dummy output to allow step ordering
    args = parser.parse_args()

    # Print out the arguments
    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    run = Run.get_context()
    try:
        main_wrapper(args, logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)  # wait for AppInsights to send telemetry

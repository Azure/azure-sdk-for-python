# Troubleshoot AI Evaluation SDK Issues

This guide walks you through how to investigate failures, common errors in the `azure-ai-evaluation` SDK, and steps to mitigate these issues.

## Table of Contents

- [Handle Evaluate API Errors](#handle-evaluate-api-errors)
  - [Troubleshoot Remote Tracking Issues](#troubleshoot-remote-tracking-issues)
  - [Troubleshoot Column Mapping Issues](#troubleshoot-column-mapping-issues)
  - [Troubleshoot Safety Evaluator Issues](#troubleshoot-safety-evaluator-issues)
  - [Troubleshoot Quality Evaluator Issues](#troubleshoot-quality-evaluator-issues)
- [Handle Simulation Errors](#handle-simulation-errors)
  - [Adversarial Simulation Supported Regions](#adversarial-simulation-supported-regions)
  - [Need to generate simulations for specific harm type](#need-to-generate-simulations-for-specific-harm-type)
  - [Simulator is slow](#simulator-is-slow)
- [Handle RedTeam Errors](#handle-redteam-errors)
  - [Permission or authentication failures](#permission-or-authentication-failures)
  - [Target resource not found](#target-resource-not-found)
  - [Agent name not found](#agent-name-not-found)
  - [Insufficient Storage Permissions](#insufficient-storage-permissions)
  - [PyRIT "Error sending prompt" message](#pyrit-error-sending-prompt-message)
- [Logging](#logging)
- [Get Additional Help](#get-additional-help)

## Handle Evaluate API Errors

### Troubleshoot Remote Tracking Issues

- Before running `evaluate()`, to ensure that you can enable logging and tracing to your Azure AI project, make sure you are first logged in by running `az login`.

- Ensure that you assign the proper permissions to the storage account linked to your Azure AI Studio hub. This can be done with the following command. More information can be found [here](https://aka.ms/credentialleshub).

    ```Shell
    # <mySubscriptionID>: Subscription ID of the Azure AI Studio hub's linked storage account (available in Azure AI hub resource view in Azure Portal).
    # <myResourceGroupName>: Resource group of the Azure AI Studio hub's linked storage account.
    # <user-id>: User object ID for role assignment (retrieve with "az ad user show" command).

    az role assignment create --role "Storage Blob Data Contributor" --scope /subscriptions/<mySubscriptionID>/resourceGroups/<myResourceGroupName> --assignee-principal-type User --assignee-object-id "<user-id>"
    ```

- Additionally, if you're using a virtual network or private link, and your evaluation run upload fails because of that, check out this [guide](https://docs.microsoft.com/azure/machine-learning/how-to-enable-studio-virtual-network#access-data-using-the-studio).

### Troubleshoot Column Mapping Issues

- When using `column_mapping` parameter in evaluators, ensure all keys and values are non-empty strings and contain only alphanumeric characters. Empty strings, non-string values, or non-alphanumeric characters can cause serialization errors and issues in downstream applications. Example of valid mapping: `{"query": "${data.query}", "response": "${data.response}"}`.

### Troubleshoot Safety Evaluator Issues

- Risk and safety evaluators depend on the Azure AI Studio safety evaluation backend service. For a list of supported regions, please refer to the documentation [here](https://aka.ms/azureaisafetyeval-regionsupport).
- If you encounter a 403 Unauthorized error when using safety evaluators, verify that you have the `Contributor` role assigned to your Azure AI project. `Contributor` role is currently required to run safety evaluations.

## Handle Simulation Errors

### Adversarial Simulation Supported Regions

Adversarial simulators use Azure AI Studio safety evaluation backend service to generate an adversarial dataset against your application. For a list of supported regions, please refer to the documentation [here](https://aka.ms/azureaiadvsimulator-regionsupport).

### Need to generate simulations for specific harm type

The Adversarial simulator does not support selecting individual harms, instead we recommend running the `AdversarialSimulator` for 4x the number of specific harms as the `max_simulation_results`

### Simulator is slow

Identify the type of simulations being run (adversarial or non-adversarial).
Adjust parameters such as `api_call_retry_sleep_sec`, `api_call_delay_sec`, and `concurrent_async_task`. Please note that rate limits to llm calls can be both tokens per minute and requests per minute.

## Handle RedTeam errors

### Permission or authentication failures
- Run `az login` in the active shell before starting the scan and ensure the account has the **Azure AI User** role plus the `Storage Blob Data Contributor` assignment on the linked storage account. Both are required to create evaluation runs and upload artifacts.
- In secured hubs, confirm the linked storage account allows access from your network (or private endpoint) and that Entra ID authentication is enabled on the storage resource.
- If the helper warns `This may be due to missing environment variables or insufficient permissions.`, double-check the `AZURE_PROJECT_ENDPOINT`, `AGENT_NAME`, and storage role assignments before retrying.

### Target resource not found
- When initializing an Azure OpenAI deployment directly as the `target`, specify `azure_endpoint` as `https://<hub>.openai.azure.com/openai/deployments/<deployment_name>/chat/completions?api-version=2025-01-01-preview`.
- If you instantiate `AzureOpenAI`, use the resource-level endpoint format `https://<hub>.openai.azure.com/` and ensure the deployment name plus API version match an active deployment.
- A cloud run error such as `Error code: 404 - {'error': {'code': '404', 'message': 'Resource not found'}}` when creating the eval group can also indicate that `azure-ai-projects>=2.0.0b1` is not installed. Upgrade to that version or later to access the preview APIs used by Red Team.

### Agent name not found
- `(not_found) Agent <name> doesn’t exist` means the Azure AI project could not resolve the agent `name`. Names are case sensitive and differ from display names.
- Verify the `AZURE_PROJECT_ENDPOINT` points to the correct project and that the agent is published there.
- Requires `DefaultAzureCredential` from `azure.identity` and `AIProjectClient` from `azure.ai.projects`.
- Use the following helper to list agents in the current project and confirm the `name` column matches your `AGENT_NAME` value:

    ```python
    def list_project_agents(endpoint: str | None = None) -> None:
        project_endpoint = endpoint or os.environ.get("AZURE_PROJECT_ENDPOINT") or ""
        if not project_endpoint:
            print("Set AZURE_PROJECT_ENDPOINT before listing agents.")
            return
        with DefaultAzureCredential() as project_credential:
            with AIProjectClient(
                endpoint=project_endpoint,
                credential=project_credential,
                api_version="2025-11-15-preview",
            ) as project_client:
                agents = list(project_client.agents.list())
        if not agents:
            print(f"No agents found in project: {project_endpoint}")
            return
        print(f"Agents in {project_endpoint}:")
        for agent in agents:
            display_name = agent.get("display_name") if isinstance(agent, dict) else getattr(agent, "display_name", "")
            name = agent.get("name") if isinstance(agent, dict) else getattr(agent, "name", "")
            print(f"- name: {name} | display_name: {display_name}")
    ```

### Insufficient Storage Permissions
- `WARNING: Failed to log artifacts to MLFlow: (UserError) Failed to upload evaluation run to the cloud due to insufficient permission to access the storage` means the linked storage account is missing the necessary assignments.
- Portal steps:
  1. Open the resource group tied to the Azure AI Project in the Azure Portal.
  2. Locate the linked storage account(s).
  3. Select each storage account and choose **Access control (IAM)**.
  4. Grant the affected identity the **Storage Blob Data Contributor** role.
- Prefer CLI? Reuse the `az role assignment create` command described in [Troubleshoot Remote Tracking Issues](#troubleshoot-remote-tracking-issues).

### PyRIT "Error sending prompt" message
- `Exception: Error sending prompt with conversation ID: <guid>` is raised by PyRIT when a target LLM call fails inside the `PromptSendingOrchestrator`. The runner retries the conversation up to the configured limit, so occasional occurrences usually resolve automatically.
- Common triggers include transient network issues, 429 throttling, or 5xx responses from the target deployment. Even if retries succeed you will still see the stack trace in notebook output.
- Inspect the `redteam.log` file written to the scan output directory (typically `<working dir>/runs/<scan_id>/redteam.log`) for the underlying exception and HTTP status. Increase verbosity with `DEBUG=True` for deeper diagnostics.
- Running in Azure AI Studio? Navigate to **Evaluate > Red Team > <run name> > Logs**, download `redteam.log`, and search for the conversation ID to inspect the payload.
- If one conversation ID keeps failing after retries, verify the target credentials, check deployment health, and review Azure OpenAI quota or rate-limit alerts in the Azure portal.

## Logging

You can set logging level via environment variable `PF_LOGGING_LEVEL`, valid values include `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`; default is `INFO`.

## Get Additional Help

Additional information on ways to reach out for support can be found in the [SUPPORT.md](https://github.com/Azure/azure-sdk-for-python/blob/main/SUPPORT.md) at the root of the repo.

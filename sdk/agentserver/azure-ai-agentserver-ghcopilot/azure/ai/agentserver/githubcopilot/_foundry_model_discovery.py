"""Azure AI Foundry model discovery and selection.

Fetches available model deployments from Azure AI Foundry and allows users to select models.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FoundryDeployment:
    """Represents an Azure AI Foundry model deployment."""

    def __init__(
        self, name: str, model_name: str, model_version: str,
        model_format: str = "", status: str = "Succeeded", token_rate_limit: int = 0,
        capabilities: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.model_name = model_name
        self.model_version = model_version
        self.model_format = model_format or "OpenAI"  # Default to OpenAI/Azure format
        self.status = status
        self.token_rate_limit = token_rate_limit  # Tokens per minute
        self.capabilities = capabilities or {}

    @property
    def supports_responses(self) -> bool:
        return self.capabilities.get("responses") in ("true", True)

    @property
    def supports_chat(self) -> bool:
        return (
            self.capabilities.get("chatCompletion") in ("true", True)
            or self.capabilities.get("chat_completion") in ("true", True)
        )

    @property
    def wire_api(self) -> str:
        """Return the appropriate wire API based on model capabilities."""
        if self.supports_responses:
            return "responses"
        # Fall back to cached wire_api if capabilities weren't available
        cached = getattr(self, "_cached_wire_api", None)
        if cached:
            return cached
        return "completions"

    def __repr__(self):
        return (
            f"{self.name} ({self.model_name} {self.model_version}"
            f" - {self.model_format}, {self.token_rate_limit} TPM, wire_api={self.wire_api})"
        )


async def discover_foundry_deployments(
    resource_url: str,
    access_token: str,
    project_endpoint: Optional[str] = None,
    management_token: Optional[str] = None,
) -> List[FoundryDeployment]:
    """Discover available model deployments from Azure AI Foundry.

    Uses Azure Management API (ARM) as the primary method, with OpenAI API fallback.
    Results are automatically sorted by token rate limit (highest first), then by
    model format preference (OpenAI > Anthropic > Meta), then alphabetically.

    Args:
        resource_url: Azure AI Foundry resource URL (e.g., https://xxx.cognitiveservices.azure.com)
        access_token: Azure access token with cognitiveservices.azure.com scope
        project_endpoint: Optional project endpoint (not used for discovery, kept for compatibility)
        management_token: Optional Azure Management API token (required for primary method)

    Returns:
        List of available chat-capable deployments, sorted by capacity (rate limit desc)
    """
    try:
        # Try Management API first (most reliable for deployments)
        if management_token:
            from urllib.parse import urlparse
            parsed = urlparse(resource_url)
            resource_name = parsed.hostname.split('.')[0] if parsed.hostname else None

            if resource_name:
                logger.info(f"Trying Azure Management API for resource: {resource_name}")
                deployments = await _discover_via_management_api(resource_name, management_token)
                if deployments:
                    return deployments
                logger.warning("Management API discovery returned no deployments")

        # Fallback: Try resource-level OpenAI API
        logger.info(f"Trying OpenAI API discovery: {resource_url}")
        deployments = await _discover_via_openai_api(resource_url, access_token)
        if deployments:
            return deployments
        logger.warning("OpenAI API discovery returned no deployments")

        logger.warning("All discovery methods failed to find deployments")
        return []

    except Exception as e:
        logger.warning(f"Failed to discover Foundry deployments: {e}")
        return []


async def _discover_via_management_api(resource_name: str, management_token: str) -> List[FoundryDeployment]:
    """Discover deployments using Azure Management API (ARM).

    Uses Azure Resource Graph to quickly find the resource across all subscriptions,
    then fetches deployments using the Management API.

    Args:
        resource_name: Cognitive Services account name (e.g., valeriepham-3194-resource)
        management_token: Azure Management API token

    Returns:
        List of chat-capable deployments
    """
    try:
        import aiohttp

        base_url = "https://management.azure.com"
        api_version = "2023-05-01"

        headers = {
            "Authorization": f"Bearer {management_token}",
            "Content-Type": "application/json"
        }

        # Validate resource_name to prevent Kusto injection
        if not re.match(r'^[a-zA-Z0-9\-]+$', resource_name):
            logger.warning(f"Invalid resource name (contains unexpected characters): {resource_name!r}")
            return []

        logger.info(f"Searching for resource: {resource_name} via Resource Graph")

        async with aiohttp.ClientSession() as session:
            # Use Azure Resource Graph to find the resource across all subscriptions
            resource_graph_url = f"{base_url}/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01"

            query_body = {
                "query": (
                    f"Resources | where type == 'microsoft.cognitiveservices/accounts'"
                    f" and name == '{resource_name}'"
                    f" | project id, subscriptionId, resourceGroup, location"
                )
            }

            async with session.post(resource_graph_url, headers=headers, json=query_body) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.warning(f"Resource Graph query failed: {response.status} - {error[:200]}")
                    return []

                graph_data = await response.json()
                resources = graph_data.get("data", [])

                if not resources:
                    logger.warning(f"Resource '{resource_name}' not found via Resource Graph")
                    return []

                # Found the resource!
                resource_info = resources[0]
                resource_id = resource_info.get("id")
                subscription_id = resource_info.get("subscriptionId")
                resource_group = resource_info.get("resourceGroup")
                location = resource_info.get("location")

                logger.info(f"Found resource via Resource Graph: {resource_id}")
                logger.info(
                    f"  Subscription: {subscription_id}, RG: {resource_group}, Location: {location}"
                )

                # Now fetch deployments for this resource
                deployments_url = f"{base_url}{resource_id}/deployments?api-version={api_version}"

                async with session.get(deployments_url, headers=headers) as deploy_response:
                    if deploy_response.status != 200:
                        error = await deploy_response.text()
                        logger.warning(f"Failed to get deployments: {deploy_response.status} - {error[:200]}")
                        return []

                    deploy_data = await deploy_response.json()

                    # Parse deployments
                    deployments = []
                    items = deploy_data.get("value", [])

                    logger.info(f"Found {len(items)} deployment(s)")

                    for item in items:
                        name = item.get("name", "unknown")
                        properties = item.get("properties", {})
                        model = properties.get("model", {})

                        model_name = model.get("name", "unknown")
                        model_version = model.get("version", "")
                        model_format = model.get("format", "")

                        # Filter: chat-capable or responses-capable models
                        capabilities = properties.get("capabilities", {})

                        is_chat = (
                            capabilities.get("chatCompletion") in ("true", True)
                            or capabilities.get("chat_completion") in ("true", True)
                        )
                        is_responses = capabilities.get("responses") in ("true", True)

                        if not is_chat and not is_responses:
                            logger.debug(f"Skipping model without chat/responses: {name} (capabilities: {capabilities})")
                            continue

                        # Note: no model_format filter — capability check above is sufficient

                        # Extract rate limits (tokens per minute)
                        rate_limits = properties.get("rateLimits", [])
                        token_rate_limit = 0
                        for limit in rate_limits:
                            if limit.get("key") == "token":
                                token_rate_limit = limit.get("count", 0)
                                break

                        # Include this model
                        deployment = FoundryDeployment(
                            name=name,
                            model_name=model_name,
                            model_version=model_version,
                            model_format=model_format,
                            status=properties.get("provisioningState", "Unknown"),
                            token_rate_limit=token_rate_limit,
                            capabilities=capabilities,
                        )
                        deployments.append(deployment)

                    if deployments:
                        # Sort by rate limits (highest first), then by format preference
                        format_priority = {"OpenAI": 3, "Anthropic": 2, "Meta": 1}

                        deployments.sort(
                            key=lambda d: (
                                d.token_rate_limit,  # Primary: highest rate limit
                                format_priority.get(d.model_format, 0),  # Secondary: format preference
                                d.name  # Tertiary: alphabetical
                            ),
                            reverse=True
                        )

                        logger.info(f"Discovered {len(deployments)} chat deployment(s) via Management API")
                        logger.info(
                            f"Selected model: {deployments[0].name} ({deployments[0].token_rate_limit} TPM)"
                        )
                        return deployments
                    else:
                        logger.warning("No chat-capable deployments found")
                        return []

    except Exception as e:
        logger.error(f"Management API discovery failed: {e}", exc_info=True)
        return []


async def _discover_via_openai_api(resource_url: str, access_token: str) -> List[FoundryDeployment]:
    """Discover deployments using OpenAI-compatible API endpoint.

    Args:
        resource_url: Foundry resource URL (e.g., https://xxx.cognitiveservices.azure.com)
        access_token: Azure access token

    Returns:
        List of chat-capable deployments
    """
    logger.info(f"Starting OpenAI API discovery for: {resource_url}")
    try:
        from urllib.parse import urlparse

        import aiohttp

        # Try multiple endpoint formats and API versions
        parsed = urlparse(resource_url)
        hostname = parsed.hostname or ""
        hostname_parts = hostname.split('.')
        resource_name = hostname_parts[0]

        # Try different URL formats and paths
        url_formats = [
            (f"{resource_url.rstrip('/')}/openai/deployments", "deployments"),
            (f"{resource_url.rstrip('/')}/openai/models", "models"),
            (f"https://{resource_name}.openai.azure.com/openai/deployments", "deployments"),
            (f"https://{resource_name}.openai.azure.com/openai/models", "models"),
        ]

        api_versions = ["2024-02-01", "2023-05-15", "2023-12-01-preview", "2024-06-01"]

        headers = {
            "Authorization": f"Bearer {access_token}",
            "api-key": access_token,  # Some endpoints expect api-key header
            "Content-Type": "application/json"
        }

        logger.info(f"Testing {len(url_formats)} OpenAI API endpoints with {len(api_versions)} API versions each")

        async with aiohttp.ClientSession() as session:
            for url, endpoint_type in url_formats:
                logger.info(f"Trying {endpoint_type} endpoint: {url}")

                for api_version in api_versions:
                    params = {"api-version": api_version}

                    async with session.get(url, headers=headers, params=params) as response:
                        response_text = await response.text()

                        if response.status == 200:
                            logger.info(f"HTTP 200 from OpenAI API: {url}?api-version={api_version}")

                            if not response_text or response_text.strip() == "":
                                logger.warning(f"Empty response from: {url}?api-version={api_version}")
                                continue

                            logger.info(f"Response preview: {response_text[:500]}")

                            try:
                                data = json.loads(response_text)
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse JSON: {e}")
                                logger.warning(f"Response was: {response_text[:500]}")
                                continue

                            logger.info(f"Response keys: {list(data.keys())}")

                            # Parse OpenAI API response
                            deployments = []
                            items = data.get("data", []) or data.get("value", [])

                            logger.info(f"Found {len(items)} items")

                            for item in items:
                                # Handle both models and deployments response formats
                                name = item.get("id") or item.get("name", "unknown")
                                model_name = item.get("model") or item.get("id", "unknown")
                                model_format = item.get("format", "")

                                logger.info(f"Found deployment: {name} (model: {model_name}, format: {model_format})")

                                # Filter: chat-capable or responses-capable models
                                capabilities = item.get("capabilities", {})

                                is_chat = (
                                    capabilities.get("chatCompletion") in ("true", True)
                                    or capabilities.get("chat_completion") in ("true", True)
                                )
                                is_responses = capabilities.get("responses") in ("true", True)

                                if not is_chat and not is_responses:
                                    logger.debug(f"Skipping model without chat/responses: {name} (capabilities: {capabilities})")
                                    continue

                                # Note: no model_format filter — capability check above is sufficient

                                # Extract rate limits (tokens per minute)
                                rate_limits = item.get("rateLimits", [])
                                token_rate_limit = 0
                                for limit in rate_limits:
                                    if limit.get("key") == "token":
                                        token_rate_limit = limit.get("count", 0)
                                        break

                                deployment = FoundryDeployment(
                                    name=name,
                                    model_name=model_name,
                                    model_version="",
                                    model_format=model_format,
                                    status="Succeeded",
                                    token_rate_limit=token_rate_limit,
                                    capabilities=capabilities,
                                )
                                deployments.append(deployment)

                            if deployments:
                                # Sort by rate limits (highest first), then by format preference
                                format_priority = {"OpenAI": 3, "Anthropic": 2, "Meta": 1}

                                deployments.sort(
                                    key=lambda d: (
                                        d.token_rate_limit,  # Primary: highest rate limit
                                        format_priority.get(d.model_format, 0),  # Secondary: format preference
                                        d.name  # Tertiary: alphabetical
                                    ),
                                    reverse=True
                                )

                                logger.info(f"Discovered {len(deployments)} chat deployments via OpenAI API")
                                logger.info(
                                    f"Selected model: {deployments[0].name}"
                                    f" ({deployments[0].token_rate_limit} TPM)"
                                )
                                return deployments
                            else:
                                logger.warning("No chat-capable deployments found in response")
                        else:
                            # Only log non-404 errors
                            if response.status != 404:
                                logger.debug(f"Status {response.status}: {response_text[:100]}")

            logger.warning(
                f"All OpenAI API endpoints failed. "
                f"Tried {len(url_formats)} URLs x {len(api_versions)} API versions"
            )
            return []

    except Exception as e:
        logger.error(f"OpenAI API discovery error: {e}", exc_info=True)
        return []




def select_model_interactive(deployments: List[FoundryDeployment]) -> Optional[str]:
    """Let user select a model interactively.

    Args:
        deployments: List of available deployments (sorted by rate limit)

    Returns:
        Selected deployment name or None
    """
    if not deployments:
        return None

    print("\n📋 Available Foundry Models (sorted by rate limit):")
    for i, deployment in enumerate(deployments, 1):
        tpm_str = f"{deployment.token_rate_limit:,} TPM" if deployment.token_rate_limit > 0 else "Unknown TPM"
        print(f"  {i}. {deployment.name}")
        print(f"     Model: {deployment.model_name} {deployment.model_version}")
        print(f"     Format: {deployment.model_format}, Rate: {tpm_str}")

    while True:
        try:
            choice = input("\nSelect model (number or name): ").strip()

            # Try as number
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(deployments):
                    return deployments[idx].name

            # Try as name
            for deployment in deployments:
                if deployment.name.lower() == choice.lower():
                    return deployment.name

            print("Invalid selection. Please try again.")

        except (KeyboardInterrupt, EOFError):
            print("\nSelection cancelled.")
            return None


def get_default_model(deployments: List[FoundryDeployment]) -> Optional[str]:
    """Select the best model from discovered deployments.

    Deployments are already sorted by the discovery process:
    1. Token rate limit (highest TPM first)
    2. Model format preference (OpenAI > Anthropic > Meta)
    3. Alphabetical name

    This function simply returns the first (highest-capacity) deployment.

    Args:
        deployments: List of chat-capable deployments (pre-sorted by rate limit)

    Returns:
        Best deployment name (highest capacity), or None if no deployments
    """
    if not deployments:
        return None

    # Deployments are already sorted by rate limit (highest first)
    # Just return the first one
    selected = deployments[0]

    logger.info(f"Auto-selecting model with highest capacity from {len(deployments)} deployment(s)")
    logger.info(f"Selected: {selected.name} ({selected.token_rate_limit:,} TPM, format: {selected.model_format})")

    # Log alternatives for visibility
    if len(deployments) > 1:
        alternatives = ", ".join([
            f"{d.name} ({d.token_rate_limit:,} TPM)"
            for d in deployments[1:4]
        ])
        logger.info(f"Other options: {alternatives}")

    return selected.name

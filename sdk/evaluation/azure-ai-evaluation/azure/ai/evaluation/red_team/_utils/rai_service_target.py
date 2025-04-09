# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import uuid
from typing import Dict, Optional, Any

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation.simulator._model_tools._generated_rai_client import GeneratedRAIClient
from pyrit.models import PromptRequestResponse, construct_response_from_request
from pyrit.prompt_target import PromptChatTarget

logger = logging.getLogger(__name__)
USER_AGENT = "azure-ai-evaluation-redteam"


class SimulationRequestDTO:
    """DTO for simulation request."""
    
    def __init__(
        self,
        *,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        params: Dict[str, str],
        templatekey: str,
        template_parameters: Dict[str, Any]
    ) -> None:
        self.url = url
        self.headers = headers
        self.payload = payload
        self.params = params
        self.templatekey = templatekey
        self.template_parameters = template_parameters
        
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON."""
        return {
            "url": self.url,
            "headers": self.headers,
            "payload": self.payload,
            "params": self.params,
            "templatekey": self.templatekey,
            "template_parameters": self.template_parameters
        }


class AzureRAIServiceTarget(PromptChatTarget):
    """Target for Azure RAI service."""
    
    def __init__(
        self,
        *,
        client: GeneratedRAIClient,
        api_version: Optional[str] = None,
        model: Optional[str] = None,
        objective: Optional[str] = None,
    ) -> None:
        """Initialize the target.
        
        :param client: The RAI client
        :param api_version: The API version to use
        :param model: The model to use
        :param objective: The objective of the target
        """
        PromptChatTarget.__init__(self)
        self._client = client
        self._api_version = api_version
        self._model = model
        self.objective = objective
        self.crescendo_template_key = "orchestrators/crescendo/crescendo_variant_1.yaml"

    def _create_async_client(self):
        """Create an async client."""
        return self._client._create_async_client()
    
    async def get_response_from_service_llm(self):
        """
        async with get_async_http_client().with_policies(retry_policy=retry_policy) as exp_retry_client:
            token = await self._client.token_manager.get_token_async()
            proxy_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            }
            response = await exp_retry_client.get(  # pylint: disable=too-many-function-args,unexpected-keyword-arg
                self.result_url, headers=proxy_headers
            )
            return response.json()
            
        """
        pass

        
    async def send_prompt_async(self, *, prompt_request: PromptRequestResponse, objective: str = "") -> PromptRequestResponse:
        """Send a prompt to the Azure RAI service.
        
        :param prompt_request: The prompt request
        :return: The response
        """
        # Add main entry point debugger when DEBUG=True
        import os
        if os.environ.get('DEBUG') == 'True':
            import pdb
            logger.info("DEBUG enabled, starting main debugger at entry point...")
            print("\n\n=========== MAIN DEBUGGER ACTIVE ===========")
            print(f"Prompt request: {prompt_request}")
            print(f"Client: {self._client}")
            print(f"Model: {self._model}")
            print("Available steps to debug:")
            print("1. Continue execution with 'c'")
            print("2. Step into next line with 's'")
            print("3. View variables with 'p <variable_name>'")
            print("4. Set a breakpoint with 'b <line_number>'")
            print("==============================================\n\n")
            pdb.set_trace()
            
        self._validate_request(prompt_request=prompt_request)
        request = prompt_request.request_pieces[0]

        logger.info(f"Sending the following prompt to the prompt target: {request}")

        # Extract prompt content
        prompt = prompt_request.request_pieces[0].converted_value
        
        # Create messages for the chat API
        # For simplicity, we'll send the prompt as a user message
        messages = [{"role": "user", "content": prompt}]
        
        # Add debugging output to help diagnose issues
        logger.debug(f"Using RAI client: {type(self._client).__name__}")
        logger.debug(f"Sending messages: {messages}")
        
        try:
            # Don't forget to import asyncio for the sleep calls
            import asyncio
            logger.info(f"About to send completion request using RAI client with model={self._model or 'gpt-4'}")
            # Use the proper submit_simulation method from the RAI client
            # This creates a long-running operation that we need to poll for results
            
            # Create a properly formatted SimulationDTO object
            # As defined in _models.py
            import json
            # prepend this to messages: {"role": "system", "content": "{{ch_template_placeholder}}"},
            messages = [{"role": "system", "content": "{{ch_template_placeholder}}"}] + messages
            body = {
                "templateKey": self.crescendo_template_key,
                "templateParameters": {
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "objective": self.objective,
                    "max_turns": 5,
                },
                "json": json.dumps({
                    "messages": messages,
                }),
                # Optional fields according to SimulationDTO
                "headers": {
                    "Content-Type": "application/json",
                    "X-CV": f"{uuid.uuid4()}",
                },
                "params": {},
                "simulationType": "Default"
            }
            
            logger.debug(f"Sending simulation request with body: {body}")
            
            # Submit the simulation request - this returns a LongRunningResponse object, not an awaitable
            # We don't use await here since it's not an async method
            import pdb;pdb.set_trace()  # Set a breakpoint here for debugging
            long_running_response = self._client._client.rai_svc.submit_simulation(body=body)
            logger.debug(f"Received long running response: {long_running_response}")
            
            # Simple and direct approach to extract operation ID from the location URL
            operation_id = None
            
            # Check if the long_running_response is a dictionary with a 'location' field
            if long_running_response.get("location", None):
                location_url = long_running_response['location']
                logger.info(f"Found location URL in response: {location_url}")
                
                # Extract the operation ID from the URL path
                import re
                # Look for the operations/UUID pattern in the URL
                match = re.search(r'/operations/([^/?]+)', location_url)
                if match:
                    # Extract the matched UUID
                    operation_id = match.group(1)
                    logger.info(f"Successfully extracted operation ID: {operation_id}")
            
            # If we have a location URL but couldn't extract an operation ID, try other methods
            if operation_id is None:
                if hasattr(long_running_response, "id"):
                    operation_id = long_running_response.id
                    logger.info(f"Using operation ID from response.id: {operation_id}")
                elif hasattr(long_running_response, "operation_id"):
                    operation_id = long_running_response.operation_id
                    logger.info(f"Using operation ID from response.operation_id: {operation_id}")
                
            # If we couldn't extract an operation ID, try more aggressive extraction methods
            if operation_id is None:
                # We will use the operation ID from the path as a last-ditch effort
                if isinstance(long_running_response, dict) and 'location' in long_running_response:
                    location_url = long_running_response['location']
                    # Try to extract operation ID from the URL more reliably
                    import re
                    # Look for any UUID-like string in the URL
                    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                    uuid_match = re.search(uuid_pattern, location_url, re.IGNORECASE)
                    if uuid_match:
                        operation_id = uuid_match.group(0)
                        logger.warning(f"UUID pattern extraction: {operation_id}")
                    else:
                        # Just grab the last part of the path as the operation ID
                        operation_id = location_url.rstrip('/').split('/')[-1]
                        logger.warning(f"Last resort operation ID extraction: {operation_id}")
                    
                    # Log successful extraction
                    logger.info(f"Successfully extracted operation ID: {operation_id}")
                else:
                    raise ValueError(f"No operation ID found in response: {long_running_response}")
                
            logger.info(f"Got operation ID: {operation_id}. Polling for result...")
            
            # Poll for the operation result
            max_retries = 10
            retry_delay = 2  # seconds
            
            for retry in range(max_retries):
                try:
                    import requests
                    
                    token = self._client.token_manager.get_token("https://management.azure.com/.default")
                    proxy_headers = {
                        "Authorization": f"Bearer {token.token}",
                        "Content-Type": "application/json",
                        "User-Agent": USER_AGENT,
                    }
                    pdb.set_trace()  # Set a breakpoint here for debugging
                    ops_result = requests.get(location_url, headers=proxy_headers)
                    operation_result = self._client._client.rai_svc.get_operation_result(operation_id=operation_id, api_key=token, headers=proxy_headers)

                    
                    logger.debug(f"Got operation result: {operation_result}")
                    await asyncio.sleep(retry_delay)
                except Exception as e:
                    pdb.set_trace()  # Set a breakpoint here for debugging
                    logger.warning(f"Error polling for operation result: {str(e)}")
                    await asyncio.sleep(retry_delay)
            pdb.set_trace() 
            response = operation_result
            # Process the response from the client
            logger.debug(f"Received final response: {response}")
            
            # Extract the content from the response
            if isinstance(response, dict) and "choices" in response and len(response["choices"]) > 0:
                if "message" in response["choices"][0] and "content" in response["choices"][0]["message"]:
                    response_text = response["choices"][0]["message"]["content"]
                elif "text" in response["choices"][0]:
                    # Some RAI services return text directly in the choices
                    response_text = response["choices"][0]["text"]
                else:
                    # Fallback: convert the entire response to a string
                    logger.warning("Unexpected response format - using string representation")
                    response_text = str(response)
            else:
                # Fallback: convert the entire response to a string
                logger.warning("Response doesn't contain expected 'choices' structure - using string representation")
                response_text = str(response)
                
            logger.info(f"Extracted response text: {response_text[:100]}...")  # Truncate long responses
                
            # Create the response entry
            response_entry = construct_response_from_request(request=request, response_text_pieces=[response_text])
            logger.info(f"Returning response entry to caller")
            return response_entry
            
        except Exception as e:
            logger.error(f"Error making API call: {str(e)}")
            # Add detailed exception info for debugging
            import traceback
            logger.debug(f"Exception details: {traceback.format_exc()}")
            
            raise EvaluationException(
                message="Failed to communicate with Azure AI service",
                internal_message=str(e),
                target=ErrorTarget.RAI_CLIENT,
                category=ErrorCategory.SERVICE_UNAVAILABLE, 
                blame=ErrorBlame.SYSTEM_ERROR,
            )

    def _validate_request(self, *, prompt_request: PromptRequestResponse) -> None:
        """Validate the request.
        
        :param prompt_request: The prompt request
        """
        if len(prompt_request.request_pieces) != 1:
            raise ValueError("This target only supports a single prompt request piece.")

        if prompt_request.request_pieces[0].converted_value_data_type != "text":
            raise ValueError("This target only supports text prompt input.")
            
    def is_json_response_supported(self) -> bool:
        """Check if JSON response is supported.
        
        :return: True if JSON response is supported, False otherwise
        """
        # This target supports JSON responses
        return True
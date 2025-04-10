# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import uuid
import os
import json
import traceback
import asyncio
import re
from typing import Dict, Optional, Any, Tuple, List

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation.simulator._model_tools._generated_rai_client import GeneratedRAIClient
from pyrit.models import PromptRequestResponse, construct_response_from_request
from pyrit.prompt_target import PromptChatTarget

# Set up file logger
def setup_file_logger(name="rai_service_target"):
    """Set up a file logger that writes to the redteam.log file"""
    logger = logging.getLogger(name)
    
    # Only set up handlers if they don't exist already
    if not logger.handlers:
        # Set base level to DEBUG to capture all logs
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # Don't pass to parent logger
        
        # Find the redteam.log file in the current directory or parent directories
        log_path = None
        current_dir = os.getcwd()
        
        # Try to find existing redteam.log in current or parent directories
        for _ in range(3):  # Try current directory and up to 2 levels up
            test_path = os.path.join(current_dir, "redteam.log")
            if os.path.exists(test_path):
                log_path = test_path
                break
            # Also look for hidden scan directories
            for dir_name in os.listdir(current_dir):
                if dir_name.startswith("scan_") or dir_name.startswith(".scan_"):
                    scan_log = os.path.join(current_dir, dir_name, "redteam.log")
                    if os.path.exists(scan_log):
                        log_path = scan_log
                        break
            
            # Move up one directory
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached the root directory
                break
            current_dir = parent_dir
                
        # If not found, create in current directory
        if not log_path:
            log_path = os.path.join(os.getcwd(), "redteam.log")
            
        # Create file handler
        file_handler = logging.FileHandler(log_path, mode='a')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
    return logger

# Create logger instance
logger = setup_file_logger("rai_service_target")
USER_AGENT = "azure-ai-evaluation-redteam"

# Create a special handler to capture PyRIT library messages
def capture_pyrit_messages():
    """Capture messages from PyRIT libraries and route them to our logger"""
    # Configure all loggers we want to capture
    pyrit_loggers = [
        "pyrit.orchestrator.multi_turn.crescendo_orchestrator",
        "pyrit.exceptions",
        "pyrit.prompt_target",
        "pyrit.orchestrator.multi_turn",
        "pyrit.orchestrator.single_turn",
    ]
    
    for logger_name in pyrit_loggers:
        pyrit_logger = logging.getLogger(logger_name)
        pyrit_logger.handlers = []  # Remove existing handlers
        pyrit_logger.propagate = False
        
        # Create a handler that forwards messages to our logger
        class LogForwarder(logging.Handler):
            def emit(self, record):
                # Format the message
                msg = self.format(record)
                level = record.levelno
                
                # Forward to our logger with appropriate level
                if level >= logging.ERROR:
                    logger.error(f"[{record.name}] {msg}")
                elif level >= logging.WARNING:
                    logger.warning(f"[{record.name}] {msg}")
                elif level >= logging.INFO:
                    logger.info(f"[{record.name}] {msg}")
                else:
                    logger.debug(f"[{record.name}] {msg}")
                
                # If DEBUG environment variable is set, also print to console
                if os.environ.get("DEBUG", "").lower() in ("true", "1", "yes", "y"):
                    print(f"[{record.levelname}] [{record.name}] {msg}")
        
        # Add the forwarder to PyRIT logger
        forwarder = LogForwarder()
        forwarder.setLevel(logging.DEBUG)
        pyrit_logger.addHandler(forwarder)
        pyrit_logger.setLevel(logging.DEBUG)

# Activate the PyRIT message capture
capture_pyrit_messages()


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

        
    async def _create_simulation_request(self, prompt: str, objective: str) -> Dict[str, Any]:
        """Create the body for a simulation request to the RAI service.
        
        :param prompt: The prompt content
        :param objective: The objective for the simulation
        :return: The request body
        """
        # Create messages for the chat API
        messages = [{"role": "system", "content": "{{ch_template_placeholder}}"},
                   {"role": "user", "content": prompt}]
        
        # Create the request body as a properly formatted SimulationDTO object
        body = {
            "templateKey": self.crescendo_template_key,
            "templateParameters": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "objective": objective or self.objective,
                "max_turns": 5,
            },
            "json": json.dumps({
                "messages": messages,
            }),
            "headers": {
                "Content-Type": "application/json",
                "X-CV": f"{uuid.uuid4()}",
            },
            "params": {
                "api-version": "2023-07-01-preview"
            },
            "simulationType": "Default"
        }
        
        logger.debug(f"Created simulation request body: {json.dumps(body, indent=2)}")
        return body

    async def _extract_operation_id(self, long_running_response: Any) -> str:
        """Extract the operation ID from a long-running response.
        
        :param long_running_response: The response from the submit_simulation call
        :return: The operation ID
        """
        # Log object type instead of trying to JSON serialize it
        logger.debug(f"Extracting operation ID from response of type: {type(long_running_response).__name__}")
        operation_id = None
        
        # Method 1: Extract from location URL - handle both dict and object with attributes
        location_url = None
        if isinstance(long_running_response, dict) and long_running_response.get("location"):
            location_url = long_running_response['location']
            logger.debug(f"Found location URL in dict: {location_url}")
        elif hasattr(long_running_response, "location") and long_running_response.location:
            location_url = long_running_response.location
            logger.debug(f"Found location URL in object attribute: {location_url}")
            
        if location_url:
            # Try to extract operation ID from the URL path using regex
            match = re.search(r'/operations/([^/?]+)', location_url)
            if match:
                operation_id = match.group(1)
                logger.debug(f"Extracted operation ID from URL: {operation_id}")
                return operation_id
            
            # Fallback to UUID pattern search
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            uuid_match = re.search(uuid_pattern, location_url, re.IGNORECASE)
            if uuid_match:
                operation_id = uuid_match.group(0)
                logger.debug(f"Extracted operation ID using UUID pattern: {operation_id}")
                return operation_id
                
            # Last resort: use the last segment of the URL path
            parts = location_url.rstrip('/').split('/')
            if parts:
                operation_id = parts[-1]
                # Verify it's a valid UUID
                if re.match(uuid_pattern, operation_id, re.IGNORECASE):
                    logger.debug(f"Extracted operation ID from URL path: {operation_id}")
                    return operation_id
            
        # Method 2: Check for direct ID properties
        if hasattr(long_running_response, "id"):
            operation_id = long_running_response.id
            logger.debug(f"Found operation ID in response.id: {operation_id}")
            return operation_id
            
        if hasattr(long_running_response, "operation_id"):
            operation_id = long_running_response.operation_id
            logger.debug(f"Found operation ID in response.operation_id: {operation_id}")
            return operation_id
        
        # Emergency fallback: Look anywhere in the response for a UUID pattern
        try:
            # Try to get a string representation safely
            response_str = str(long_running_response)
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            uuid_matches = re.findall(uuid_pattern, response_str, re.IGNORECASE)
            if uuid_matches:
                operation_id = uuid_matches[0]
                logger.debug(f"Found UUID in response string: {operation_id}")
                return operation_id
        except Exception as e:
            logger.warning(f"Error converting response to string for UUID search: {str(e)}")
            
        # If we get here, we couldn't find an operation ID
        raise ValueError(f"Could not extract operation ID from response of type: {type(long_running_response).__name__}")

    async def _poll_operation_result(self, operation_id: str, max_retries: int = 10, retry_delay: int = 2) -> Dict[str, Any]:
        """Poll for the result of a long-running operation.
        
        :param operation_id: The operation ID to poll
        :param max_retries: Maximum number of polling attempts
        :param retry_delay: Delay in seconds between polling attempts
        :return: The operation result
        """
        logger.debug(f"Polling for operation result with ID: {operation_id}")
        
        for retry in range(max_retries):
            try:
                operation_result = self._client._client.rai_svc.get_operation_result(operation_id=operation_id)
                
                # Check if we have a valid result
                if operation_result:
                    logger.debug(f"Received operation result (attempt {retry+1}): {json.dumps(operation_result, indent=2)}")
                    return operation_result
                    
            except Exception as e:
                logger.warning(f"Error polling for operation result (attempt {retry+1}): {str(e)}")
            
            # Wait before the next attempt
            await asyncio.sleep(retry_delay)
            
        # If we've exhausted retries, return whatever we have
        return {}

    async def _process_response(self, response: Any) -> str:
        """Process and extract meaningful content from the RAI service response.
        
        :param response: The raw response from the RAI service
        :return: The extracted text content
        """
        logger.debug(f"Processing response: {response}")
        
        # Handle string responses by trying to parse as JSON first
        if isinstance(response, str):
            try:
                response = json.loads(response)
                logger.debug("Successfully parsed response string as JSON")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse response as JSON: {e}")
                # Continue with the string response
        
        # Extract text content through multiple paths
        extracted_content = None
        
        # Method 1: Standard OpenAI format with "choices"
        if isinstance(response, dict) and "choices" in response and response["choices"]:
            choice = response["choices"][0]
            
            # Check for content in message
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                logger.debug(f"Found content in message.content: {content[:100]}...")
                
                # Try to extract generated_question from JSON content
                if content.strip().startswith("{"):
                    try:
                        content_json = json.loads(content)
                        if "generated_question" in content_json:
                            extracted_content = content_json["generated_question"]
                            logger.debug(f"Extracted generated_question: {extracted_content}")
                            return extracted_content
                    except json.JSONDecodeError:
                        # The string looks like JSON but isn't valid JSON
                        logger.warning(f"Content looks like JSON but couldn't be parsed")
                        
                # If we couldn't extract generated_question, use the whole content
                extracted_content = content
                return extracted_content
                
            # Check for text directly in choice
            elif "text" in choice:
                extracted_content = choice["text"]
                logger.debug(f"Found content in choice.text: {extracted_content}")
                return extracted_content
        
        # Method 2: Look for common field names
        if isinstance(response, dict):
            for field_name in ["generated_question", "content", "text", "message"]:
                if field_name in response:
                    extracted_content = response[field_name]
                    logger.debug(f"Found content in field '{field_name}': {extracted_content}")
                    return extracted_content
        
        # Method 3: Try to extract from a nested structure
        if extracted_content is None and isinstance(response, dict):
            # Use string representation as last resort
            response_str = str(response)
            logger.warning("Using string representation of response as content")
            
            # Try to extract content using regex pattern matching
            # This is specifically handling the complex nested JSON structure we're seeing in errors
            if "'content':" in response_str:
                try:
                    # Extract content between single quotes after 'content':
                    content_match = re.search(r"'content': '([^']*)'", response_str)
                    if content_match:
                        content = content_match.group(1)
                        
                        # If the content looks like JSON, try to extract generated_question
                        if content.strip().startswith("{"):
                            try:
                                # Handle escaped quotes and newlines
                                fixed_content = content.replace("\\'", "'").replace("\\n", "\n")
                                content_json = json.loads(fixed_content)
                                
                                if "generated_question" in content_json:
                                    extracted_content = content_json["generated_question"]
                                    logger.debug(f"Extracted generated_question from regex: {extracted_content}")
                                    return extracted_content
                                else:
                                    logger.error(f"Key 'generated_question' not found in parsed JSON: {content_json}")
                            except json.JSONDecodeError:
                                logger.warning("Couldn't parse extracted content as JSON")
                        
                        # Return the content directly
                        extracted_content = content
                        logger.debug(f"Extracted content using regex: {extracted_content}")
                        return extracted_content
                except Exception as e:
                    logger.warning(f"Error extracting content with regex: {str(e)}")
        
        # Last resort fallback
        if extracted_content is None:
            extracted_content = str(response)
            logger.warning(f"Using fallback string representation: {extracted_content[:100]}...")
            
        return extracted_content

    async def send_prompt_async(self, *, prompt_request: PromptRequestResponse, objective: str = "") -> PromptRequestResponse:
        """Send a prompt to the Azure RAI service.
        
        :param prompt_request: The prompt request
        :param objective: Optional objective to use for this specific request
        :return: The response
        """
        logger.info("Starting send_prompt_async operation")
        self._validate_request(prompt_request=prompt_request)
        request = prompt_request.request_pieces[0]
        prompt = request.converted_value
        
        logger.info(f"Sending prompt to RAI service (length: {len(prompt)})")
        logger.debug(f"Prompt content: {prompt[:100]}...")  # Log only the beginning of the prompt
        
        try:
            # Step 1: Create the simulation request
            body = await self._create_simulation_request(prompt, objective)
            
            # Step 2: Submit the simulation request
            logger.info(f"Submitting simulation request to RAI service with model={self._model or 'default'}")
            long_running_response = self._client._client.rai_svc.submit_simulation(body=body)
            logger.debug(f"Received long running response: {long_running_response}")
            
            # Step 3: Extract the operation ID
            operation_id = await self._extract_operation_id(long_running_response)
            logger.info(f"Extracted operation ID: {operation_id}")
            
            # Step 4: Poll for the operation result
            operation_result = await self._poll_operation_result(operation_id)
            
            # Step 5: Process the response to extract content
            response_text = await self._process_response(operation_result)
            logger.info(f"Successfully processed response (length: {len(response_text)})")
            logger.debug(f"Response content: {response_text[:100]}...")  # Log only the beginning 
                
            # Step 6: Create and return the response entry
            response_entry = construct_response_from_request(
                request=request, 
                response_text_pieces=[response_text]
            )
            logger.info("Completed send_prompt_async operation")
            return response_entry
            
        except Exception as e:
            logger.error(f"Error in send_prompt_async: {str(e)}")
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
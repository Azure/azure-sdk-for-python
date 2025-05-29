import pytest
import unittest.mock as mock
import json
import uuid
import asyncio


try:
    import pyrit
    has_pyrit = True
except ImportError:
    has_pyrit = False

if has_pyrit:   
    from pyrit.common import initialize_pyrit, IN_MEMORY

    initialize_pyrit(memory_db_type=IN_MEMORY)
    from azure.ai.evaluation.red_team._utils._rai_service_target import AzureRAIServiceTarget
    from pyrit.models import PromptRequestResponse, PromptRequestPiece


# Basic mocks
MockGeneratedRAIClient = mock.AsyncMock()
MockLogger = mock.Mock()

# Create a special async mock for RAI service that properly resolves awaits
class ProperAsyncMock(mock.AsyncMock):
    async def __call__(self, *args, **kwargs):
        # This ensures when the mock is awaited, it returns the value directly
        return super().__call__(*args, **kwargs)

# Use our custom AsyncMock that handles awaits properly
MockRAISvc = ProperAsyncMock()

# Mock the client structure
MockGeneratedRAIClient._client.rai_svc = MockRAISvc

@pytest.fixture
def mock_prompt_request():
    piece = PromptRequestPiece(
        role="user",
        original_value="Test prompt for simulation",
        converted_value="Test prompt for simulation",
        conversation_id="sim_conv_id",
        sequence=1,
        original_value_data_type="text",
        converted_value_data_type="text",
    )
    return PromptRequestResponse(request_pieces=[piece])

@pytest.fixture
def rai_target():
    return AzureRAIServiceTarget(
        client=MockGeneratedRAIClient,
        logger=MockLogger,
        objective="Test Objective",
        prompt_template_key="test_template.yaml",
        is_one_dp_project=False
    )

@pytest.mark.asyncio
async def test_create_simulation_request(rai_target):
    """Tests the structure of the simulation request body."""
    prompt = "User prompt content"
    objective = "Specific objective"
    body = await rai_target._create_simulation_request(prompt, objective)

    assert body["templateKey"] == "test_template.yaml"
    assert body["templateParameters"]["objective"] == objective
    assert body["templateParameters"]["max_turns"] == 5 # Default
    assert body["simulationType"] == "Default"
    assert "messages" in json.loads(body["json"])
    messages = json.loads(body["json"])["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == prompt
    assert "X-CV" in body["headers"]

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_input, expected_id",
    [
        # Case 1: LongRunningResponse object with location URL
        (mock.Mock(spec=['_data'], _data={"location": "https://example.com/subscriptions/sub-id/resourceGroups/rg/providers/prov/workspaces/ws/operations/op-id-123"}), "op-id-123"),
        # Case 2: object with _data attribute containing location URL
        (mock.Mock(spec=['_data'], _data={"location": "https://example.com/ml/v2/subscriptions/sub-id/resourceGroups/rg/providers/prov/workspaces/ws/operations/op-id-456?api-version=..."}), "op-id-456"),
        # Case 3: dict with location URL
        ({"location": "https://another.com/operations/op-id-789/"}, "op-id-789"),        
        # Case 4: object with location attribute that properly converts to string
        (mock.Mock(location="https://yetanother.com/api/operations/op-id-abc", __str__=lambda self: "https://yetanother.com/api/operations/op-id-abc"), "op-id-abc"),
        # Case 5: object with id attribute - no location attribute
        (mock.Mock(spec=["id"], id="op-id-def"), "op-id-def"),
        # Case 6: object with operation_id attribute - no location attribute
        (mock.Mock(spec=["operation_id"], operation_id="op-id-ghi"), "op-id-ghi"),
        # Case 7: string URL
        ("https://final.com/operations/op-id-jkl", "op-id-jkl"),
        # Case 8: string UUID
        (str(uuid.uuid4()), str(uuid.uuid4())), # Compare type, value will differ
         # Case 9: _data with location URL (UUID only)
        (mock.Mock(spec=['_data'], _data={"location":  "https://example.com/subscriptions/sub-id/resourceGroups/rg/providers/prov/workspaces/ws/jobs/job-uuid/operations/op-uuid"}), "op-uuid"),
        ]
 )
async def test_extract_operation_id_success(rai_target, response_input, expected_id):
    """Tests various successful operation ID extractions."""
    # Special handling for UUID string case
    if isinstance(response_input, str) and len(response_input) == 36:
         extracted_id = await rai_target._extract_operation_id(response_input)
         assert isinstance(extracted_id, str)
         try:
             uuid.UUID(extracted_id)
         except ValueError:
             pytest.fail("Extracted ID is not a valid UUID")
    else:
        extracted_id = await rai_target._extract_operation_id(response_input)
        assert extracted_id == expected_id


@pytest.mark.asyncio
async def test_extract_operation_id_failure(rai_target):
    """Tests failure to extract operation ID."""
    with pytest.raises(ValueError, match="Could not extract operation ID"):
        await rai_target._extract_operation_id(mock.Mock(spec=[])) # Empty mock

@pytest.mark.asyncio
@mock.patch('asyncio.sleep', return_value=None) # Mock sleep to speed up test
async def test_poll_operation_result_success(mock_sleep, rai_target):
    """Tests successful polling."""
    operation_id = "test-op-id"
    expected_result = {"status": "succeeded", "data": "some result"}

    # Track call count outside the function
    call_count = [0]
    
    # Create a non-async function that returns dictionaries directly
    def get_operation_result(operation_id=None):
        if call_count[0] == 0:
            call_count[0] += 1
            return {"status": "running"}
        else:
            return expected_result
    
    # Replace the method in the implementation to use our non-async function
    # This is needed because _poll_operation_result expects the result directly, not as a coroutine
    rai_target._client._client.get_operation_result = get_operation_result

    result = await rai_target._poll_operation_result(operation_id)

    assert result == expected_result
    # We know it should be called twice based on our mock function
    assert call_count[0] == 1  # It's 1 because it gets incremented after first call

@pytest.mark.asyncio
@mock.patch('asyncio.sleep', return_value=None)
async def test_poll_operation_result_timeout(mock_sleep, rai_target):
    """Tests polling timeout and fallback."""
    operation_id = "timeout-op-id"
    max_retries = 3

    # Use a non-async function that returns the dict directly
    def always_running(operation_id=None):
        return {"status": "running"}
      # Replace the actual get_operation_result function with our mock
    rai_target._client._client.get_operation_result = always_running

    result = await rai_target._poll_operation_result(operation_id, max_retries=max_retries)

    assert result is None
    MockLogger.error.assert_called_with(f"Failed to get operation result after {max_retries} attempts. Last error: None")

@pytest.mark.asyncio
@mock.patch('asyncio.sleep', return_value=None)
async def test_poll_operation_result_not_found_fallback(mock_sleep, rai_target):
    """Tests fallback after multiple 'operation ID not found' errors."""
    operation_id = "not-found-op-id"
    max_retries = 5
    call_count = 0
    
    # Instead of using a mock, we'll use a regular function that raises exceptions
    # This approach ensures we're working with real exceptions that match what the implementation expects
    def operation_not_found(operation_id=None):
        nonlocal call_count
        call_count += 1
        # Real exception with the text that the implementation will check for
        raise Exception("operation id 'not-found-op-id' not found")
      # Replace the client's get_operation_result with our function
    rai_target._client._client.get_operation_result = operation_not_found

    result = await rai_target._poll_operation_result(operation_id, max_retries=max_retries)

    # The implementation should recognize the error pattern after 3 calls and return fallback
    assert call_count == 3

    assert result is None
    MockLogger.error.assert_called_with("Consistently getting 'operation ID not found' errors. Extracted ID 'not-found-op-id' may be incorrect.")

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw_response, expected_content",
    [
        # Case 1: OpenAI-like structure
        ({"choices": [{"message": {"content": '{"key": "value"}'}}]}, {"key": "value"}),
        # Case 2: Direct content (JSON string) - Fixed to match implementation
        ({"content": '{"direct": true}'}, {"direct": True}),
        # Case 3: Direct content (plain string)
        ({"content": "plain string"}, {"content": "plain string"}),
         # Case 4: Nested result structure
        ({"result": {"output": {"choices": [{"message": {"content": '{"nested": 1}'}}]}}}, {"nested": 1}),
        # Case 5: Result with direct content
        ({"result": {"content": '{"result_content": "yes"}'}}, {"result_content": "yes"}),
        # Case 6: Plain string response (parsable as dict)
        ('{"string_dict": "parsed"}', {"string_dict": "parsed"}),
        # Case 7: Plain string response (not JSON)
        ("Just a string", {"content": "Just a string"}),
        # Case 8: Object with as_dict() method
        (mock.Mock(as_dict=lambda: {"as_dict_key": "val"}), {"as_dict_key": "val"}),
        # Case 9: Empty dict
        ({}, {}),
        # Case 10: None response
        (None, {'content': 'None'}), # None is converted to string and wrapped in content dict
    ]
)
async def test_process_response(rai_target, raw_response, expected_content):
    """Tests processing of various response structures."""
    processed = await rai_target._process_response(raw_response)
    assert processed == expected_content

@pytest.mark.asyncio
@mock.patch('azure.ai.evaluation.red_team._utils._rai_service_target.AzureRAIServiceTarget._create_simulation_request')
@mock.patch('azure.ai.evaluation.red_team._utils._rai_service_target.AzureRAIServiceTarget._extract_operation_id')
@mock.patch('azure.ai.evaluation.red_team._utils._rai_service_target.AzureRAIServiceTarget._poll_operation_result')
@mock.patch('azure.ai.evaluation.red_team._utils._rai_service_target.AzureRAIServiceTarget._process_response')
async def test_send_prompt_async_success_flow(mock_process, mock_poll, mock_extract, mock_create, rai_target, mock_prompt_request):
    """Tests the successful end-to-end flow of send_prompt_async."""
    mock_create.return_value = {"body": "sim_request"}
    mock_submit_response = {"location": "mock_location"}
    
    # Create a proper synchronous function that returns the response directly
    def submit_simulation(body=None):
        return mock_submit_response
    
    # Replace the submit_simulation with our function
    rai_target._client._client.submit_simulation = submit_simulation
    
    mock_extract.return_value = "mock-op-id"
    mock_poll.return_value = {"status": "succeeded", "raw": "poll_result"}
    mock_process.return_value = {"processed": "final_content"}

    response = await rai_target.send_prompt_async(prompt_request=mock_prompt_request, objective="override_objective")

    mock_create.assert_called_once_with("Test prompt for simulation", "override_objective")
    # We're not using MockRAISvc anymore, so don't assert on it
    # Check that our extract was called with the right value
    mock_extract.assert_called_once_with(mock_submit_response)
    mock_poll.assert_called_once_with("mock-op-id")
    mock_process.assert_called_once_with({"status": "succeeded", "raw": "poll_result"})

    assert len(response.request_pieces) == 1
    response_piece = response.request_pieces[0]
    assert response_piece.role == "assistant"
    assert json.loads(response_piece.converted_value) == {"processed": "final_content"}

@pytest.mark.asyncio
async def test_send_prompt_async_exception_fallback(rai_target, mock_prompt_request, monkeypatch):
    """Tests fallback response generation on exception during send_prompt_async."""
    # Import the module to patch
    from azure.ai.evaluation.red_team._utils import _rai_service_target
    import logging
    import time
    from unittest.mock import patch
    
    # Setup a logger that we can check
    test_logger = mock.Mock()
    test_logger.error = mock.Mock()
    test_logger.debug = mock.Mock()
    test_logger.warning = mock.Mock()
    test_logger.info = mock.Mock()
    rai_target.logger = test_logger
    
    # Make sure the logger is available at the module level for the retry decorator
    monkeypatch.setattr(_rai_service_target, "logger", test_logger)
    
    # Create a counter to track how many times the exception is triggered
    call_count = 0
    
    # Create an exception-raising function that will trigger the retry mechanism
    # We use a counter to make sure it fails enough times to trigger the fallback
    # This is important - we need to replace the _extract_operation_id method since 
    # that's where the exception is most appropriate to trigger retries
    async def mock_extract_operation_id(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # Raise ValueError since that's what the retry decorator is configured to catch
        raise ValueError(f"Simulated failure #{call_count}")
      # Patch the method directly on the instance to ensure we're affecting the retry mechanism
    with patch.object(rai_target, '_extract_operation_id', side_effect=mock_extract_operation_id):
        
        # Call the function, which should trigger retries and eventually use fallback
        response = await rai_target.send_prompt_async(prompt_request=mock_prompt_request)
        
        # Verify that our exception was triggered multiple times (showing retry happened)
        assert call_count >= 5, f"Expected at least 5 retries but got {call_count}"
        
        # Verify we got a valid response with the expected structure
        assert len(response.request_pieces) == 1
        response_piece = response.request_pieces[0]
        assert response_piece.role == "assistant"
          # Check if the response is the fallback JSON with expected fields
        fallback_content = json.loads(response_piece.converted_value)
        assert "generated_question" in fallback_content
        assert "rationale_behind_jailbreak" in fallback_content

def test_validate_request_success(rai_target, mock_prompt_request):
    """Tests successful validation."""
    try:
        rai_target._validate_request(prompt_request=mock_prompt_request)
    except ValueError:
        pytest.fail("_validate_request raised ValueError unexpectedly")

def test_validate_request_invalid_pieces(rai_target, mock_prompt_request):
    """Tests validation failure with multiple pieces."""
    mock_prompt_request.request_pieces.append(mock_prompt_request.request_pieces[0]) # Add a second piece
    with pytest.raises(ValueError, match="only supports a single prompt request piece"):
        rai_target._validate_request(prompt_request=mock_prompt_request)

def test_validate_request_invalid_type(rai_target, mock_prompt_request):
    """Tests validation failure with non-text data type."""
    mock_prompt_request.request_pieces[0].converted_value_data_type = "image"
    with pytest.raises(ValueError, match="only supports text prompt input"):
        rai_target._validate_request(prompt_request=mock_prompt_request)

def test_is_json_response_supported(rai_target):
    """Tests if JSON response is supported."""
    assert rai_target.is_json_response_supported() is True

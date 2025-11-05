#!/usr/bin/env python3
"""
Custom agents samples gated test.

This module tests all Custom agent samples with parametrized test cases.
Each sample gets its own test class with multiple test scenarios.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest
import requests

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class BaseCustomAgentTest:
    """Base class for Custom agent sample tests with common utilities."""

    def __init__(self, sample_name: str, script_name: str):
        """
        Initialize test configuration.

        Args:
            sample_name: Name of the sample directory (e.g., 'simple_mock_agent')
            script_name: Name of the Python script to run (e.g., 'custom_mock_agent_test.py')
        """
        self.sample_name = sample_name
        self.script_name = script_name
        self.sample_dir = project_root / "samples" / sample_name
        self.port = self._find_free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.responses_endpoint = f"{self.base_url}/responses"
        self.process = None
        self.original_dir = os.getcwd()

    def setup(self):
        """Set up environment (dependencies are pre-installed in CI/CD)."""
        os.chdir(self.sample_dir)

    def start_server(self):
        """Start the agent server in background."""
        # Prepare environment with UTF-8 encoding to handle emoji in agent output
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["DEFAULT_AD_PORT"] = str(self.port)
        env.setdefault("AGENT_BASE_URL", self.base_url)

        # Use subprocess.DEVNULL to avoid buffering issues
        self.process = subprocess.Popen(
            [sys.executable, self.script_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

    def wait_for_ready(self, max_attempts: int = 30, delay: float = 1.0) -> bool:
        """Wait for the server to be ready."""
        for _i in range(max_attempts):
            # Check if process is still running
            if self.process and self.process.poll() is not None:
                # Process has terminated
                print(f"Server process terminated unexpectedly with exit code {self.process.returncode}")
                return False

            try:
                response = requests.get(f"{self.base_url}/readiness", timeout=1)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass

            try:
                response = requests.get(self.base_url, timeout=1)
                if response.status_code in [200, 404]:
                    return True
            except requests.exceptions.RequestException:
                pass

            time.sleep(delay)

        # Server didn't start - print diagnostics
        if self.process:
            self.process.terminate()
            stdout, stderr = self.process.communicate(timeout=5)
            print(f"Server failed to start. Logs:\n{stdout}\nErrors:\n{stderr}")

        return False

    def send_request(self, input_data: Any, stream: bool = False, timeout: int = 30) -> requests.Response:
        """
        Send a request to the agent.

        Args:
            input_data: Input to send (string or structured message)
            stream: Whether to use streaming
            timeout: Request timeout in seconds

        Returns:
            Response object
        """
        payload = {
            "agent": {"name": "mock_agent", "type": "agent_reference"},
            "input": input_data,
            "stream": stream,
        }

        # Note: Only set stream parameter for requests.post if streaming is requested
        # Otherwise, let requests handle response body reading with timeout
        if stream:
            return requests.post(self.responses_endpoint, json=payload, timeout=timeout, stream=True)
        else:
            return requests.post(self.responses_endpoint, json=payload, timeout=timeout)

    def cleanup(self):
        """Clean up resources and restore directory."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                self.process.kill()

        os.chdir(self.original_dir)

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]


class TestSimpleMockAgent:
    """Test suite for Simple Mock Agent - uses shared server."""

    @pytest.fixture(scope="class")
    def mock_server(self):
        """Shared server instance for all mock agent tests."""
        tester = BaseCustomAgentTest("simple_mock_agent", "custom_mock_agent_test.py")
        tester.setup()
        tester.start_server()

        if not tester.wait_for_ready():
            tester.cleanup()
            pytest.fail("Simple Mock Agent server failed to start")

        yield tester
        tester.cleanup()

    @pytest.mark.parametrize(
        "input_text,expected_keywords,description",
        [
            ("Hello, mock agent!", ["mock"], "simple_greeting"),
            ("Test message", ["mock"], "test_message"),
            ("What can you do?", ["mock"], "capability_query"),
        ],
    )
    def test_mock_agent_queries(self, mock_server, input_text: str, expected_keywords: list, description: str):
        """Test mock agent with various queries."""
        response = mock_server.send_request(input_text, stream=False)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_text = response.text.lower()
        found_keyword = any(kw.lower() in response_text for kw in expected_keywords)
        assert found_keyword, f"Expected one of {expected_keywords} in response"

    def test_streaming_response(self, mock_server):
        """Test mock agent with streaming response."""
        response = mock_server.send_request("Hello, streaming test!", stream=True)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Verify we can read streaming data
        lines_read = 0
        for line in response.iter_lines():
            if line:
                lines_read += 1
                if lines_read >= 3:
                    break

        assert lines_read > 0, "Expected to read at least one line from streaming response"


@pytest.mark.skip
class TestMcpSimple:
    """Test suite for Custom MCP Simple - uses Microsoft Learn MCP."""

    @pytest.fixture(scope="class")
    def mcp_server(self):
        """Shared server instance for all MCP Simple tests."""
        tester = BaseCustomAgentTest("mcp_simple", "mcp_simple.py")
        tester.setup()
        tester.start_server()

        if not tester.wait_for_ready():
            tester.cleanup()
            pytest.fail("MCP Simple server failed to start")

        yield tester
        tester.cleanup()

    @pytest.mark.parametrize(
        "input_text,expected_keywords,description",
        [
            (
                "What Azure services can I use for image generation?",
                ["image", "generation", "azure"],
                "image_generation",
            ),
            (
                "Show me documentation about Azure App Service",
                ["app", "service", "azure"],
                "app_service_docs",
            ),
        ],
    )
    def test_mcp_operations(self, mcp_server, input_text: str, expected_keywords: list, description: str):
        """Test MCP Simple with Microsoft Learn queries."""
        response = mcp_server.send_request(input_text, stream=False, timeout=60)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_text = response.text.lower()
        found_keyword = any(kw.lower() in response_text for kw in expected_keywords)
        assert found_keyword, f"Expected one of {expected_keywords} in response"


@pytest.mark.skip
class TestBilingualWeekendPlanner:
    """Test suite for the bilingual weekend planner custom sample."""

    @pytest.fixture(scope="class")
    def weekend_planner_server(self):
        """Shared server fixture for bilingual weekend planner tests."""
        pytest.importorskip("azure.identity")
        pytest.importorskip("agents")
        pytest.importorskip("openai")

        tester = BaseCustomAgentTest("bilingual_weekend_planner", "main.py")
        tester.setup()

        env_overrides = {
            "API_HOST": "github",
            "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", "unit-test-token"),
            "GITHUB_OPENAI_BASE_URL": os.environ.get("GITHUB_OPENAI_BASE_URL", "http://127.0.0.1:65535"),
            "WEEKEND_PLANNER_MODE": "container",
        }
        original_env = {key: os.environ.get(key) for key in env_overrides}
        os.environ.update(env_overrides)

        try:
            tester.start_server()

            if not tester.wait_for_ready(max_attempts=60, delay=1.0):
                tester.cleanup()
                pytest.fail("Bilingual weekend planner server failed to start")

            yield tester
        finally:
            tester.cleanup()
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_offline_planner_response(self, weekend_planner_server):
        """Verify the planner responds with a graceful error when the model is unreachable."""
        response = weekend_planner_server.send_request("Plan my weekend in Seattle", stream=False, timeout=60)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_text = response.text.lower()
        assert "error running agent" in response_text

    def test_streaming_offline_response(self, weekend_planner_server):
        """Verify streaming responses deliver data even when the model call fails."""
        response = weekend_planner_server.send_request("Planifica mi fin de semana en Madrid", stream=True, timeout=60)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        lines_read = 0
        for line in response.iter_lines():
            if line:
                lines_read += 1
                if lines_read >= 3:
                    break

        assert lines_read > 0, "Expected to read at least one line from streaming response"

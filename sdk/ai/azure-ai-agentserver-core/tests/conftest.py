"""
Pytest configuration for samples gated tests.

This file automatically loads environment variables from .env file
and provides shared test fixtures.
"""

import json
import logging
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import requests
from dotenv import load_dotenv

# Load .env file from project root or current directory
# conftest.py is at: src/adapter/python/tests/gated_test/conftest.py
# Need to go up 6 levels to reach project root
project_root = Path(__file__).parent.parent
env_paths = [
    project_root / ".env",  # Project root
    Path.cwd() / ".env",  # Current working directory
    Path(__file__).parent / ".env",  # Test directory
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class AgentTestClient:
    """Generic test client for all agent types."""

    def __init__(
        self,
        sample_name: str,
        script_name: str,
        endpoint: str = "/responses",  # Default endpoint
        base_url: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: int = 120,
        port: Optional[int] = None,
    ):
        self.sample_name = sample_name
        self.script_name = script_name
        self.endpoint = endpoint
        self.timeout = timeout

        # Setup paths
        self.project_root = project_root  # Use already defined project_root
        self.sample_dir = self.project_root / "samples" / sample_name
        self.original_dir = os.getcwd()

        # Determine port assignment priority: explicit param > env override > random
        if env_vars and env_vars.get("DEFAULT_AD_PORT"):
            self.port = int(env_vars["DEFAULT_AD_PORT"])
        elif port is not None:
            self.port = port
        else:
            self.port = self._find_free_port()

        # Configure base URL for client requests
        self.base_url = (base_url or f"http://127.0.0.1:{self.port}").rstrip("/")

        # Setup environment
        # Get Agent Framework configuration (new format)
        azure_ai_project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
        azure_ai_model_deployment = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")
        agent_project_name = os.getenv("AGENT_PROJECT_NAME", "")

        # Get legacy Azure OpenAI configuration (for backward compatibility)
        main_api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        main_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        main_api_version = os.getenv("OPENAI_API_VERSION", "2025-03-01-preview")
        embedding_api_version = os.getenv("AZURE_OPENAI_EMBEDDINGS_API_VERSION", "2024-02-01")

        self.env_vars = {
            "PYTHONIOENCODING": "utf-8",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONUNBUFFERED": "1",
            # Agent Framework environment variables (new)
            "AZURE_AI_PROJECT_ENDPOINT": azure_ai_project_endpoint,
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": azure_ai_model_deployment,
            "AGENT_PROJECT_NAME": agent_project_name,
            # Legacy Azure OpenAI environment variables (for backward compatibility)
            "AZURE_OPENAI_API_KEY": main_api_key,
            "AZURE_OPENAI_ENDPOINT": main_endpoint,
            "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", ""),
            "OPENAI_API_VERSION": main_api_version,
        }

        # Auto-configure embeddings to use main config if not explicitly set
        # This allows using the same Azure OpenAI resource for both chat and embeddings
        self.env_vars["AZURE_OPENAI_EMBEDDINGS_API_KEY"] = os.getenv(
            "AZURE_OPENAI_EMBEDDINGS_API_KEY",
            main_api_key,  # Fallback to main API key
        )
        self.env_vars["AZURE_OPENAI_EMBEDDINGS_ENDPOINT"] = os.getenv(
            "AZURE_OPENAI_EMBEDDINGS_ENDPOINT",
            main_endpoint,  # Fallback to main endpoint
        )
        self.env_vars["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME"] = os.getenv(
            "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", ""
        )
        self.env_vars["AZURE_OPENAI_EMBEDDINGS_API_VERSION"] = os.getenv(
            "AZURE_OPENAI_EMBEDDINGS_API_VERSION",
            embedding_api_version,  # Fallback to main API version
        )
        self.env_vars["AZURE_OPENAI_EMBEDDINGS_MODEL_NAME"] = os.getenv(
            "AZURE_OPENAI_EMBEDDINGS_MODEL_NAME",
            os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", ""),  # Fallback to deployment name
        )

        if env_vars:
            self.env_vars.update(env_vars)

        # Ensure server picks the dynamically assigned port and clients know how to reach it
        self.env_vars.setdefault("DEFAULT_AD_PORT", str(self.port))
        self.env_vars.setdefault("AGENT_BASE_URL", self.base_url)

        self.process = None
        self.session = requests.Session()

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def setup(self):
        """Setup test environment."""
        os.chdir(self.sample_dir)

        logger.info(
            "Configured %s to listen on %s",
            self.sample_name,
            f"{self.base_url}{self.endpoint}",
        )

        # Validate critical environment variables
        # For Agent Framework samples, check new env vars first
        required_vars = []
        if "agent_framework" in self.sample_name:
            # Agent Framework samples use new format
            required_vars = [
                "AZURE_AI_PROJECT_ENDPOINT",
                "AZURE_AI_MODEL_DEPLOYMENT_NAME",
            ]
        else:
            # Legacy samples use old format
            required_vars = [
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
            ]

        missing_vars = []
        for var in required_vars:
            value = self.env_vars.get(var) or os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                logger.debug(f"Environment variable {var} is set")

        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error(f"Sample name: {self.sample_name}")
            if "agent_framework" in self.sample_name:
                logger.error("For Agent Framework samples, please set:")
                logger.error("  - AZURE_AI_PROJECT_ENDPOINT")
                logger.error("  - AZURE_AI_MODEL_DEPLOYMENT_NAME")
            pytest.skip(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Set environment variables
        for key, value in self.env_vars.items():
            if value:  # Only set if value is not empty
                os.environ[key] = value

        # Start server
        self.start_server()

        # Wait for server to be ready
        if not self.wait_for_ready():
            self.cleanup()
            logger.error(f"{self.sample_name} server failed to start")
            pytest.skip(f"{self.sample_name} server failed to start")

    def start_server(self):
        """Start the agent server."""
        logger.info(
            "Starting %s server in %s on port %s",
            self.sample_name,
            self.sample_dir,
            self.port,
        )

        env = os.environ.copy()
        env.update(self.env_vars)
        env["DEFAULT_AD_PORT"] = str(self.port)
        env.setdefault("AGENT_BASE_URL", self.base_url)

        # Use unbuffered output to capture logs in real-time
        self.process = subprocess.Popen(
            [sys.executable, "-u", self.script_name],  # -u for unbuffered output
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,  # Line buffered
        )
        logger.info(f"Server process started with PID {self.process.pid}")

    def wait_for_ready(self, max_attempts: int = 30, delay: float = 1.0) -> bool:
        """Wait for server to be ready."""
        logger.info(
            "Waiting for server to be ready at %s (max %s attempts)",
            f"{self.base_url}{self.endpoint}",
            max_attempts,
        )

        for i in range(max_attempts):
            # Check process status first
            if self.process.poll() is not None:
                # Process has terminated - read all output
                stdout, stderr = self.process.communicate()
                logger.error(f"Server terminated with code {self.process.returncode}")
                logger.error("=== SERVER OUTPUT ===")
                if stdout:
                    logger.error(stdout)
                if stderr:
                    logger.error("=== STDERR ===")
                    logger.error(stderr)
                return False

            # Read and log any available output
            self._log_server_output()

            # Check health endpoint
            try:
                health_response = self.session.get(f"{self.base_url}/readiness", timeout=2)
                if health_response.status_code == 200:
                    logger.info(f"Server ready after {i + 1} attempts")
                    return True
                else:
                    logger.debug(f"Health check attempt {i + 1}: status {health_response.status_code}")
            except Exception as e:
                logger.debug(f"Health check attempt {i + 1} failed: {e}")
                # After several failed attempts, show server output for debugging
                if i > 5 and i % 5 == 0:
                    logger.warning(f"Server still not ready after {i + 1} attempts, checking output...")
                    self._log_server_output(force=True)

            time.sleep(delay)

        # Timeout reached - dump all server output
        logger.error(f"Server failed to start within {max_attempts} attempts")
        self._dump_server_output()
        return False

    def cleanup(self):
        """Cleanup resources."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                self.process.kill()

        os.chdir(self.original_dir)

    def request(
        self,
        input_data: Any,
        stream: bool = False,
        timeout: Optional[int] = None,
        debug: bool = False,
    ) -> requests.Response:
        """Send request to the server."""
        url = f"{self.base_url}{self.endpoint}"
        timeout = timeout or self.timeout

        payload = {"input": input_data, "stream": stream}

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json; charset=utf-8",
        }

        if debug:
            logger.info(f">>> POST {url}")
            logger.info(f">>> Headers: {headers}")
            logger.info(f">>> Payload: {json.dumps(payload, indent=2)}")

        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=timeout, stream=stream)

            if debug:
                logger.info(f"<<< Status: {response.status_code}")
                logger.info(f"<<< Headers: {dict(response.headers)}")

                # For non-streaming responses, log the body
                if not stream:
                    try:
                        content = response.json()
                        logger.info(f"<<< Body: {json.dumps(content, indent=2)}")
                    except (ValueError, requests.exceptions.JSONDecodeError):
                        logger.info(f"<<< Body: {response.text}")

            return response

        except Exception as e:
            logger.error(f"Request failed: {e}")
            self._log_server_output()
            raise

    def _log_server_output(self, force=False):
        """Log server output for debugging."""
        if self.process and self.process.poll() is None and hasattr(self.process, "stdout"):
            try:
                import select

                if hasattr(select, "select"):
                    # Use non-blocking read
                    ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                    if ready:
                        # Read available lines without blocking
                        import fcntl
                        import os as os_module

                        # Set non-blocking mode
                        fd = self.process.stdout.fileno()
                        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os_module.O_NONBLOCK)

                        try:
                            while True:
                                line = self.process.stdout.readline()
                                if not line:
                                    break
                                line = line.strip()
                                if line:
                                    if force or any(
                                        keyword in line.lower()
                                        for keyword in [
                                            "error",
                                            "exception",
                                            "traceback",
                                            "failed",
                                        ]
                                    ):
                                        logger.error(f"Server output: {line}")
                                    else:
                                        logger.info(f"Server output: {line}")
                        except BlockingIOError:
                            pass  # No more data available
            except Exception as e:
                if force:
                    logger.debug(f"Could not read server output: {e}")

    def _dump_server_output(self):
        """Dump all remaining server output."""
        if self.process:
            try:
                # Try to read any remaining output
                if self.process.poll() is None:
                    # Process still running, terminate and get output
                    self.process.terminate()
                    try:
                        stdout, stderr = self.process.communicate(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        stdout, stderr = self.process.communicate()
                else:
                    stdout, stderr = self.process.communicate()

                if stdout:
                    logger.error(f"=== FULL SERVER OUTPUT ===\n{stdout}")
                if stderr:
                    logger.error(f"=== FULL SERVER STDERR ===\n{stderr}")
            except Exception as e:
                logger.error(f"Failed to dump server output: {e}")


@pytest.fixture
def basic_client():
    """Fixture for basic agent tests."""
    client = AgentTestClient(
        sample_name="agent_framework/basic_simple",
        script_name="minimal_example.py",
        endpoint="/responses",
        timeout=60,
    )
    client.setup()
    yield client
    client.cleanup()


@pytest.fixture
def workflow_client():
    """Fixture for workflow agent tests (reflection pattern with Worker + Reviewer)."""
    client = AgentTestClient(
        sample_name="agent_framework/workflow_agent_simple",
        script_name="workflow_agent_simple.py",
        endpoint="/responses",  # Changed from /runs to /responses
        timeout=600,  # Increased timeout for workflow agent (reflection loop may need multiple iterations)
    )
    client.setup()
    yield client
    client.cleanup()


@pytest.fixture
def mcp_client():
    """Fixture for MCP simple agent tests (uses Microsoft Learn MCP, no auth required)."""
    client = AgentTestClient(
        sample_name="agent_framework/mcp_simple",
        script_name="mcp_simple.py",
        endpoint="/responses",  # Changed from /runs to /responses
        timeout=120,
    )
    client.setup()
    yield client
    client.cleanup()


@pytest.fixture
def mcp_apikey_client():
    """Fixture for MCP API Key agent tests (uses GitHub MCP, requires GITHUB_TOKEN)."""
    client = AgentTestClient(
        sample_name="agent_framework/mcp_apikey",
        script_name="mcp_apikey.py",
        endpoint="/responses",  # Changed from /runs to /responses
        timeout=120,
        env_vars={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")},
    )
    client.setup()
    yield client
    client.cleanup()

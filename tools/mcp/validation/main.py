from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Dict, List, Optional, Any
import logging
import sys
import os
from pathlib import Path

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

# Log the Python executable and environment information
logger.info(f"Running with Python executable: {sys.executable}")
logger.info(f"Virtual environment path: {os.environ.get('VIRTUAL_ENV', 'Not running in a virtual environment')}")
logger.info(f"Working directory: {os.getcwd()}")

_REPO_ROOT = Path(__file__).parents[3]
_TOX_INI_PATH = os.path.abspath(_REPO_ROOT / "eng" / "tox" / "tox.ini")

# Initialize server
mcp = FastMCP("validation")

def run_command(command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """Run a command and return the result."""
    logger.info(f"Running command: {' '.join(command)}")
    logger.info(f"Virtual environment path: {os.environ.get('VIRTUAL_ENV', 'Not running in a virtual environment')}")
    
    try:
        if not cwd:
            cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            logger.info(f"Using current working directory: {cwd}")
        
        # On Windows, use shell=True for better command handling
        use_cmd = os.name == "nt"
        
        if use_cmd:
            # Convert list to single command string for Windows shell
            command = ["cmd.exe", "/c"] + command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
            )
        else:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=cwd,
            )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "code": 1,
        }

@mcp.tool("verify_setup")
def verify_setup_tool(venv: Optional[str] = None) -> Dict[str, Any]:
    """Verify machine is set up correctly for development.
    
    Args:
        venv: Optional venv to check for installed dependencies
    """
    def verify_installation(command: List[str], name: str) -> Dict[str, Any]:
        """Helper function to verify installation of a tool."""
        logger.info(f"Checking installation of {name} with command: {command}")
        
        result = run_command(command)
        
        if not result["success"]:
            logger.error(f"{name} verification failed. Exit code: {result['code']}")
            logger.error(f"stderr: {result['stderr']}")
            return {
                "success": False,
                "message": f"{name} is not installed or not available in PATH.",
                "details": {
                    "stdout": result["stdout"].split(f"{name}: commands")[1] if f"{name}: commands" in result["stdout"] else result["stdout"],
                    "stderr": result["stderr"],
                    "exit_code": result["code"]
                }
            }
            
        version_output = result["stdout"].strip() or "No version output"
        logger.info(f"{name} version output: '{version_output}'")
        
        return {
            "success": True,
            "message": f"{name} is installed. Version: {version_output}"
        }

    results = {
        "node": verify_installation(["node", "--version"], "Node.js"),
        "python": verify_installation(["python", "--version"], "Python")
    }

    # Check if tox is installed
    logger.info("Checking tox installation...")
    
    tox_command = ["tox", "--version", "-c", _TOX_INI_PATH]
    results["tox"] = verify_installation(tox_command, "tox")

    return results


@mcp.tool("tox")
def tox_tool(package_path: str, environment: str, config_file: Optional[str] = None) -> Dict[str, Any]:
    """Run tox tests on a Python package.
    
    Args:
        package_path: Path to the Python package to test
        environment: tox environment to run (e.g., 'pylint', 'mypy')
        config_file: Optional path to a tox configuration file
    """
    # Normalize config file path
    config_path = config_file if config_file is not None else _TOX_INI_PATH
    
    command = ["tox", "run"]
        
    command.extend(["-e", environment])
    command.extend(["-c", config_path])
    command.extend(["--root", package_path])
    
    logger.info(f"Running tox with command: {command}")
    logger.info(f"Working directory: {package_path}")
    
    return run_command(command, cwd=package_path)

# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
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

_REPO_ROOT = Path(__file__).parents[3]
_TOX_INI_PATH = os.path.abspath(_REPO_ROOT / "eng" / "tox" / "tox.ini")

# Initialize FastMCP server
mcp = FastMCP("validation")

def run_command(command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """Run a command and return the result."""
    logger.info(f"Running command: {' '.join(command)}")
    try:
        if not cwd:
            cwd = os.getcwd()
            logger.info(f"Using current working directory: {cwd}")
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "code": e.returncode,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool("verify_setup")
def verify_setup_tool(venv: Optional[str] = None) -> Dict[str, Any]:
    """Verify machine is set up correctly for development.
    
    Args:
        venv: Optional venv to check for installed dependencies
    """
    def verify_installation(command: List[str], name: str) -> Dict[str, Any]:
        """Helper function to verify installation of a tool."""
        result = run_command(command)
        if not result["success"]:
            logger.error(f"{name} is not installed or not available in PATH.")
            return {
                "success": False,
                "message": f"{name} is not installed or not available in PATH."
            }
        logger.info(f"{name} version: {result['stdout'].strip()}")
        return {
            "success": True,
            "message": f"{name} is installed. Version: {result['stdout'].strip()}"
        }

    results = {
        "node": verify_installation(["node", "--version"], "Node.js"),
        "python": verify_installation(["python", "--version"], "Python")
    }

    # Check if tox is installed
    if venv:
        logger.info(f"Using virtual environment: {venv}")
        tox_command = [os.path.join(venv, "bin", "tox"), "--version"] if os.name != "nt" else [os.path.join(venv, "Scripts", "tox.exe"), "--version", "-c", _TOX_INI_PATH, "--root", str(_REPO_ROOT)]
    else:
        tox_command = ["tox", "--version", "-c", _TOX_INI_PATH]

    results["tox"] = verify_installation(tox_command, "tox")

    return results


@mcp.tool("tox")
def tox_tool(package_path: str, environment: Optional[str] = None, config_file: Optional[str] = None) -> Dict[str, Any]:
    """Run tox tests on a Python package.
    
    Args:
        package_path: Path to the Python package to test
        environment: Optional tox environment to run (e.g., 'pylint', 'mypy')
        config_file: Optional path to a tox configuration file
    """
    command = ["tox", "run"]
    if environment:
        command.extend(["-e", environment])
    if config_file:
        command.extend(["-c", config_file or _TOX_INI_PATH])
    command.extend(["--root", package_path])
    return run_command(command, cwd=package_path)

# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
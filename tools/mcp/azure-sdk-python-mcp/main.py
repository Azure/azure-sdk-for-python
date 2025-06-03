from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Dict, List, Optional, Any
import logging
import sys
import os
import re
from pathlib import Path
from github import Github

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

# Log environment information
logger.info(f"Running with Python executable: {sys.executable}")
logger.info(f"Virtual environment path: {os.environ.get('VIRTUAL_ENV', 'Not running in a virtual environment')}")
logger.info(f"Working directory: {os.getcwd()}")

# Initialize constants
# Initialize with a default path that will be updated if needed
_REPO_ROOT = None
_TOX_INI_PATH = None

# Initialize server
mcp = FastMCP("azure-sdk-python-mcp")

def _ensure_repo_root_set() -> str:
    """Ensure the repository root is set and return it.
    
    Returns:
        The repository root path
        
    Raises:
        RuntimeError: If repository root has not been set
    """
    if _REPO_ROOT is None:
        raise RuntimeError("Repository root not set. Call get_python_repo_root tool first.")
    return _REPO_ROOT

@mcp.tool("get_python_repo_root")
def get_python_repo_root(repo_path: str) -> Dict[str, Any]:
    """Get the root directory of the Python repository.
    
    Args:
        repo_path: Path to the azure-sdk-for-python repository
        
    Returns:
        Dictionary with success status and repository information
    """
    global _REPO_ROOT, _TOX_INI_PATH
    
    try:
        # Validate the path exists
        if not os.path.exists(repo_path):
            return {
                "success": False,
                "message": f"Path does not exist: {repo_path}"
            }
        
        # Check if it's actually the azure-sdk-for-python repository
        # Look for key indicators
        indicators = [
            "setup.py",
            "sdk",
            "tools",
            "eng/tox/tox.ini"
        ]
        
        for indicator in indicators:
            indicator_path = os.path.join(repo_path, indicator)
            if not os.path.exists(indicator_path):
                return {
                    "success": False,
                    "message": f"Could not find Azure SDK for Python repository root. Missing: {indicator}"
                }
        
        # Set the global variables
        _REPO_ROOT = os.path.abspath(repo_path)
        _TOX_INI_PATH = os.path.join(_REPO_ROOT, "eng", "tox", "tox.ini")
        
        logger.info(f"Repository root set to: {_REPO_ROOT}")
        logger.info(f"Tox config path set to: {_TOX_INI_PATH}")
        
        return {
            "success": True,
            "message": f"Repository root set to: {_REPO_ROOT}",
            "repo_root": _REPO_ROOT,
            "tox_ini_path": _TOX_INI_PATH
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error setting repository root: {str(e)}"
        }

def run_command(command: List[str], cwd: Optional[str] = None, is_typespec: bool = False, 
               typespec_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run a command and return the result.
    
    Args:
        command: The command to run as a list of strings
        cwd: Optional working directory to run the command in
        is_typespec: Whether this is a TypeSpec CLI command
        typespec_args: Optional arguments for TypeSpec commands
    
    Returns:
        Dictionary with command execution results
    """
    # Handle TypeSpec commands
    if is_typespec:
        # Build TypeSpec CLI command
        if os.name == "nt":  # Windows
            cli_cmd = ["cmd.exe", "/C", "npx", "@azure-tools/typespec-client-generator-cli"] + command
        else:  # Unix/Linux/MacOS
            cli_cmd = ["npx", "@azure-tools/typespec-client-generator-cli"] + command
            
        # Add TypeSpec arguments
        if typespec_args:
            for key, value in typespec_args.items():
                cli_cmd.append(f"--{key}")
                cli_cmd.append(str(value))
                
        command = cli_cmd
      # Log the command
    logger.info(f"Running command: {' '.join(command)}")
    
    try:
        # Set default working directory if not provided
        if not cwd:
            cwd = _ensure_repo_root_set()
            logger.info(f"Using repository root as working directory: {cwd}")
        
        # Handle Windows command prefix if not a TypeSpec command
        if os.name == "nt" and not is_typespec:
            command = ["cmd.exe", "/C"] + command
        
        # Execute command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
        )
        
        if result.stdout:
            logger.info(f"Command output excerpt: {result.stdout[:100]}...")
        
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
def verify_setup_tool() -> Dict[str, Any]:
    """Verify machine is set up correctly for development."""
    def verify_installation(command: List[str], name: str) -> Dict[str, Any]:
        """Helper function to verify installation of a tool."""
        logger.info(f"Checking installation of {name}")
        result = run_command(command)
        
        if not result["success"]:
            return {
                "success": False,
                "message": f"{name} is not installed or not available in PATH.",
                "details": {
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                    "exit_code": result["code"]
                }
            }
            
        version_output = result["stdout"].strip() or "No version output"
        return {
            "success": True,
            "message": f"{name} is installed. Version: {version_output}"
        }

    try:
        # Ensure repository root is set
        _ensure_repo_root_set()
        
        # Verify required tools
        results = {
            "node": verify_installation(["node", "--version"], "Node.js"),
            "python": verify_installation(["python", "--version"], "Python"),
            "tox": verify_installation(["tox", "--version", "-c", _TOX_INI_PATH], "tox")
        }

        return results
        
    except RuntimeError as e:
        return {
            "success": False,
            "message": str(e)
        }

@mcp.tool("tox")
def tox_tool(package_path: str, environment: str, config_file: Optional[str] = None) -> Dict[str, Any]:
    """Run tox tests on a Python package.
    
    Args:
        package_path: Path to the Python package to test
        environment: tox environment to run (e.g., 'pylint', 'mypy')
        config_file: Optional path to a tox configuration file
    """
    try:
        # Ensure repository root is set
        _ensure_repo_root_set()
        
        # Use default config path if not provided
        config_path = config_file if config_file is not None else _TOX_INI_PATH
        
        # Build and run tox command
        command = ["tox", "run", "-e", environment, "-c", config_path, "--root", package_path]
        return run_command(command, cwd=package_path)
        
    except RuntimeError as e:
        return {
            "success": False,
            "message": str(e),
            "stdout": "",
            "stderr": "",
            "code": 1
        }

def get_latest_commit(tspurl: str) -> str:
    """Get the latest commit hash for a given TypeSpec config URL.
    
    Args:
        tspurl: The URL to the tspconfig.yaml file.
        
    Returns:
        The URL with the latest commit hash for the specified TypeSpec configuration.
    """
    try:
        # Extract URL components using regex
        res = re.match(
            r"^https://(?P<urlRoot>github|raw.githubusercontent).com/(?P<repo>[^/]*/azure-rest-api-specs(-pr)?)/(tree/|blob/)?(?P<commit>[0-9a-f]{40}|[^/]+)/(?P<path>.*)/tspconfig.yaml$",
            tspurl
        )
        
        if res is None:
            raise ValueError(f"Invalid TypeSpec URL format: {tspurl}")
            
        groups = res.groupdict()
        commit = groups["commit"]
        
        # Parse repository information
        repo_parts = tspurl.split("/")
        repo_name = f"{repo_parts[3]}/{repo_parts[4]}"
        
        # Get path within repo
        parts = tspurl.split("azure-rest-api-specs/blob/")[1].split("/")
        parts.pop(0)  # Remove branch name
        folder_path = "/".join(parts)

        # If commit is a branch name (not a SHA), get latest commit
        if not commit or commit == "main" or len(commit) != 40:
            g = Github()
            repo = g.get_repo(repo_name)
            commits = repo.get_commits(path=folder_path)
            
            if not commits:
                raise ValueError(f"No commits found for path: {folder_path}")

            latest_commit = commits[0].sha
            return f"https://raw.githubusercontent.com/{groups['repo']}/{latest_commit}/{groups['path']}/tspconfig.yaml"
            
        return f"https://raw.githubusercontent.com/{groups['repo']}/{commit}/{groups['path']}/tspconfig.yaml"

    except Exception as e:
        logger.error(f"Error getting latest commit: {str(e)}")
        raise

@mcp.tool("init")
def init_tool(tsp_config_url: str) -> Dict[str, Any]:
    """Initializes and generates a typespec client library directory given the url.
    
    Args:
        tsp_config_url: The URL to the tspconfig.yaml file.    
    Returns:
        A dictionary containing the result of the command.
    """
    try:
        # Ensure repository root is set
        repo_root = _ensure_repo_root_set()
        
        # Get updated URL with latest commit hash
        updated_url = get_latest_commit(tsp_config_url)
        
        # Run the init command using the combined function
        return run_command(["init"], cwd=repo_root, is_typespec=True, 
                          typespec_args={"tsp-config": updated_url})
                          
    except RuntimeError as e:
        return {
            "success": False,
            "message": str(e),
            "stdout": "",
            "stderr": "",
            "code": 1
        }

@mcp.tool("init_local")
def init_local_tool(tsp_config_path: str) -> Dict[str, Any]:
    """Initializes and subsequently generates a typespec client library directory from a local azure-rest-api-specs repo.

    This command is used to generate a client library from a local azure-rest-api-specs repository. No additional
    commands are needed to generate the client library.

    Args:
        tsp_config_path: The path to the local tspconfig.yaml file.

    Returns:
        A dictionary containing the result of the command.    """
    try:
        # Ensure repository root is set
        repo_root = _ensure_repo_root_set()
        
        # Run the init command with local path using the combined function
        return run_command(["init"], cwd=repo_root, is_typespec=True, 
                          typespec_args={"tsp-config": tsp_config_path})
                          
    except RuntimeError as e:
        return {
            "success": False,
            "message": str(e),
            "stdout": "",
            "stderr": "",
            "code": 1
        }

# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
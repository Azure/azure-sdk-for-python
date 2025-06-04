import logging
import sys
import os
import re
import csv
import subprocess
from io import StringIO
from typing import Dict, List, Optional, Any

import httpx
from github import Github
from mcp.server.fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("azure-sdk-python-mcp")

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

# Log environment information
logger.info(f"Running with Python executable: {sys.executable}")
logger.info(f"Virtual environment path: {os.environ.get('VIRTUAL_ENV', 'Not running in a virtual environment')}")
logger.info(f"Working directory: {os.getcwd()}")

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

def run_command(command: List[str], cwd: str, is_typespec: bool = False, 
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
def verify_setup_tool(command_path: str, tox_ini_path: str) -> Dict[str, Any]:
    """Verify machine is set up correctly for development.

    :param str command_path: Path to the command in. (i.e. ./azure-sdk-for-python/)
    :param str tox_ini_path: Path to the tox.ini file. (i.e. ./azure-sdk-for-python/eng/tox/tox.ini)
    """
    def verify_installation(command: List[str], name: str) -> Dict[str, Any]:
        """Helper function to verify installation of a tool."""
        logger.info(f"Checking installation of {name}")
        result = run_command(command, cwd=command_path)
        
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
    
    # Verify required tools
    results = {
        "node": verify_installation(["node", "--version"], "Node.js"),
        "python": verify_installation(["python", "--version"], "Python"),
        "tox": verify_installation(["tox", "--version", "-c", tox_ini_path], "tox")
    }

    return results

@mcp.tool("validation_tool")
def tox_tool(package_path: str, environment: str, repo_path: str, tox_ini_path: str) -> Dict[str, Any]:
    """Run validation steps on a Python package using tox.
    
    Args:
        package_path: Path to the Python package to test
        environment: tox environment to run (e.g., 'pylint', 'mypy')
        repo_path: Path to the repository root (i.e. ./azure-sdk-for-python/)
        tox_ini_path: Path to the tox.ini file (i.e. ./azure-sdk-for-python/eng/tox/tox.ini)
    """
    # Build and run tox command
    command = ["tox", "run", "-e", environment, "-c", tox_ini_path, "--root", package_path]
    return run_command(command, cwd=repo_path)

@mcp.tool("init")
def init_tool(tsp_config_url: str, repo_path: str) -> Dict[str, Any]:
    """Initializes and generates a typespec client library directory given the url.
    
    Args:
        tsp_config_url: The URL to the tspconfig.yaml file.
        repo_path: The path to the repository root (i.e. ./azure-sdk-for-python/).
    Returns:
        A dictionary containing the result of the command.
    """
    try:
        # Get updated URL with latest commit hash
        updated_url = get_latest_commit(tsp_config_url)
        
        # Run the init command using the combined function
        return run_command(["init"], cwd=repo_path, is_typespec=True,
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
def init_local_tool(tsp_config_path: str, repo_path:str) -> Dict[str, Any]:
    """Initializes and subsequently generates a typespec client library directory from a local azure-rest-api-specs repo.

    This command is used to generate a client library from a local azure-rest-api-specs repository. No additional
    commands are needed to generate the client library.

    Args:
        tsp_config_path: The path to the local tspconfig.yaml file.
        repo_path: The path to the repository root (i.e. ./azure-sdk-for-python/).

    Returns:
        A dictionary containing the result of the command.    """
    try:
        
        # Run the init command with local path using the combined function
        return run_command(["init"], cwd=repo_path, is_typespec=True,
                          typespec_args={"tsp-config": tsp_config_path})
                          
    except RuntimeError as e:
        return {
            "success": False,
            "message": str(e),
            "stdout": "",
            "stderr": "",
            "code": 1
        }


@mcp.tool("check_library_health")
def check_library_health(library_name: str) -> Dict[str, Any]:
    """Checks the health status of a client library.

    :param str library_name: The name of the library to check.
    :returns: A dictionary containing the result of the command.
    """

    url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/python-sdk-health-report/scripts/repo_health_status_report/health_report.csv"
    response = httpx.get(url)

    try:
        response.raise_for_status()

        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)
        
        headers = next(reader)
        column_headers = headers[1:]

        result = {}
        for row in reader:
            if row:
                key = row[0]
                values_dict = {header: value for header, value in zip(column_headers, row[1:])}
                result[key] = values_dict
        
    except httpx.HTTPError as e:
        logger.error(f"Error downloading health report: {e}")
        return {
            "success": False,
            "stderr": f"Failed to fetch health report for {library_name}. Status code: {response.status_code}",
            "stdout": "",
            "code": response.status_code
        }

    return {
        "success": True,
        "stdout": result[library_name] if library_name in result else f"No health data found for {library_name}",
        "stderr": "",
        "code": response.status_code
    }


# Run the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')

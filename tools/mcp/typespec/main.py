import re
from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Dict, Optional, Any, Match, Union
import logging
import sys
import os
from pathlib import Path
from github import Github
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

# Initialize server
mcp = FastMCP("typespec")

def get_latest_commit(tspurl: str) -> str:
    """Get the latest commit hash for a given TypeSpec config URL.
    
    Args:
        tspurl: The URL to the tspconfig.yaml file.
        
    Returns:
        The URL with the latest commit hash for the specified TypeSpec configuration.
    """
    # Extract the service name, repo, commit, and tspconfig path from the URL
    try:
        # Use regex to validate and extract components from the URL
        configUrl = tspurl
        res = re.match(
            r"^https://(?P<urlRoot>github|raw.githubusercontent).com/(?P<repo>[^/]*/azure-rest-api-specs(-pr)?)/(tree/|blob/)?(?P<commit>[0-9a-f]{40}|[^/]+)/(?P<path>.*)/tspconfig.yaml$",
            configUrl
        )
        
        commit = None
        if res is not None:
            groups = res.groupdict()
            commit = groups["commit"]
            logger.info(f"Extracted commit: {commit}")
            
        if res is None:
            raise ValueError(f"Invalid TypeSpec URL format: {tspurl}")
            
        groups = res.groupdict()
        
        # Parse the URL to extract the path within the repository
        repo_parts = tspurl.split("/")
        logger.info(f"Extracted repo parts: {repo_parts}")
        repo_name = f"{repo_parts[3]}/{repo_parts[4]}"
        
        parts = tspurl.split("azure-rest-api-specs/blob/")[1].split("/")
        parts.pop(0)  # Remove the branch name (e.g., 'main')
        
        # Join all parts until the last directory (containing tspconfig.yaml)
        folder_path = "/".join(parts)
        logger.info(f"Extracted folder path from URL: {folder_path}")

        g = Github()
        repo = g.get_repo(repo_name)

        # Get commits that affect the specific folder
        # TODO: if commit is a branch name
        if not commit or commit == "main":
            commits = repo.get_commits(path=folder_path)
            
            if not commits:
                raise ValueError(f"No commits found for path: {folder_path}")

            latest_commit = commits[0].sha
            logger.info(f"Found latest commit for {latest_commit}")
            return f"https://raw.githubusercontent.com/{groups['repo']}/{latest_commit}/{groups['path']}/tspconfig.yaml"
        return f"https://raw.githubusercontent.com/{groups['repo']}/{commit}/{groups['path']}/tspconfig.yaml"

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise
            

# Helper function to run CLI commands
def run_typespec_cli_command(command: str, args: Dict[str, Any], root_dir: Optional[str] = None) -> Dict[str, Any]:
    """Run a TypeSpec client generator CLI command and return the result."""
    # Determine if we're running on Windows and adjust command accordingly
    if os.name == "nt":  # Windows
        cli_args = ["cmd.exe", "/C", "npx", "@azure-tools/typespec-client-generator-cli", command]
    else:  # Unix/Linux/MacOS
        cli_args = ["npx", "@azure-tools/typespec-client-generator-cli", command]

    # Convert args dict to CLI arguments
    for key, value in args.items():
        cli_args.append(f"--{key}")
        cli_args.append(str(value))

    logger.info(f"Running command: {' '.join(cli_args)}")
    
    try:
        # Run the command and capture the output
        if root_dir:
            result = subprocess.run(
                cli_args,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,  # Explicitly close stdin
                cwd=root_dir,
            )
        else:
            result = subprocess.run(
                cli_args,
                capture_output=True,
                stdin=subprocess.DEVNULL,  # Explicitly close stdin
                text=True,
            )
        logger.info(f"Command output: {result.stdout}")

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except Exception as e:
        logger.error(f"Command failed with error: {str(e)}")
        logger.error(e)
        # raise
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "code": 1
        }


# Register tools for each TypeSpec client generator CLI command
@mcp.tool("init")
def init_tool(tsp_config_url: str) -> Dict[str, Any]:
    """Initializes and generates a typespec client library directory given the url.
    
    Args:
        tsp_config_url: The URL to the tspconfig.yaml file.    
    Returns:
        A dictionary containing the result of the command.
    """
    # Get the URL to the tspconfig.yaml file
    updated_url = get_latest_commit(tsp_config_url)
    
    # Prepare arguments for the CLI command
    args = {}
    args["tsp-config"] = updated_url
    
    # If root_dir is not provided, use the repository root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    logger.info(f"No root_dir provided, using repository root: {root_dir}")
    
    return run_typespec_cli_command("init", args, root_dir=root_dir)

@mcp.tool("init_local")
def init_local_tool(tsp_config_path: str, commit_id: str) -> Dict[str, Any]:
    """Generate SDK from a local azure-rest-api-specs repo and commit id.

    Args:
        tsp_config_path: The path to the local tspconfig.yaml file.
        commit_id: The commit ID of the local azure-rest-api-specs repository.

    Returns:
        A dictionary containing the result of the command.
    """
    # Prepare arguments for the CLI command
    tsp_config_path = Path(tsp_config_path).resolve().as_posix()
    
    # If root_dir is not provided, use the repository root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    logger.info(f"No root_dir provided, using repository root: {root_dir}")
    
    # install dependencies
    if os.name == "nt":
        python_interpreter = os.path.join(root_dir, ".venv", "Scripts", "python.exe")
    else:
        python_interpreter = os.path.join(root_dir, ".venv", "bin", "python")
    try:
        # create .venv if it does not exist
        venv_path = os.path.join(root_dir, ".venv")
        if not os.path.exists(venv_path):
            logger.info(f"Creating virtual environment at {venv_path}")
            subprocess.run(["python", "-m", "venv", ".venv"], check=True, cwd=root_dir)
        
        # install dependencies
        result = subprocess.run(
            [python_interpreter, "scripts/dev_setup.py", "-p", "azure-core"],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,  # Explicitly close stdin
            cwd=root_dir,
        )
        logger.info(f"Command output: {result.stdout}")
        
        # create generate_input.json
        spec_folder = tsp_config_path.split("azure-rest-api-specs")[0] + "azure-rest-api-specs"
        tsp_folder = tsp_config_path.split("azure-rest-api-specs/")[1].split("/tspconfig.yaml")[0]
        generate_input = {
            "specFolder": spec_folder,
            "headSha": commit_id,
            "repoHttpsUrl": "https://github.com/Azure/azure-rest-api-specs",
            "relatedTypeSpecProjectFolder": [tsp_folder],
        }
        generate_input_path = os.path.join(root_dir, ".venv/generate_input.json")
        generate_output_path = os.path.join(root_dir, ".venv/generate_output.json")
        generate_tmp_path = os.path.join(root_dir, ".venv/tmp.json")
        with open(generate_input_path, "w") as f:
            json.dump(generate_input, f, indent=2)
        with open(generate_tmp_path, "w") as f:
            json.dump({}, f, indent=2)
            
        # generate SDK
        result = subprocess.run(
            [python_interpreter, "-m", "packaging_tools.sdk_generator", generate_input_path, generate_tmp_path],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,  # Explicitly close stdin
            cwd=root_dir,
        )
        logger.info(f"generate sdk: {result.stdout}")
        result = subprocess.run(
            [python_interpreter, "-m", "packaging_tools.sdk_package", generate_tmp_path, generate_output_path],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,  # Explicitly close stdin
            cwd=root_dir,
        )
        logger.info(f"package sdk: {result.stdout}")
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except Exception as e:
        logger.error(f"Failed to install dependencies: {str(e)}")
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "code": 1
        }

# Run the MCP server
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
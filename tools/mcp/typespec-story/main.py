import re
from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Dict, Optional, Any, Match, Union
import logging
import sys
import os
from github import Github, Auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)
hander = logging.StreamHandler(sys.stderr)
logger.addHandler(hander)

# Initialize FastMCP server
mcp = FastMCP("typespec")

def get_latest_commit(tspurl: str) -> Union[Match[str], None]:
    """Get the latest commit hash for a given TypeSpec config URL.
    
    Args:
        tspurl: The URL to the tspconfig.yaml file.
        
    Returns:
        The latest commit hash for the specified TypeSpec configuration.
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
        if res:
            groups = res.groupdict()
            commit = groups["commit"]
            logger.info(f"Extracted commit: {commit}")
            
        # Parse the URL to extract the path within the repository
        repo_parts = tspurl.split("/")
        repo_name = f"{repo_parts[3]}/{repo_parts[4]}"
        
        parts = tspurl.split("azure-rest-api-specs/blob/")[1].split("/")
        parts.pop(0)  # Remove the branch name (e.g., 'main')
        
        # Join all parts until the last directory (containing tspconfig.yaml)
        folder_path = "/".join(parts)
        logger.info(f"Extracted folder path from URL: {folder_path}")

        auth = Auth.Token(os.getenv("GH_TOKEN"))
        g = Github(auth=auth)
        logger.info(f"Authenticated to GitHub with token: {g}")
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
    cli_args = ["npx", "@azure-tools/typespec-client-generator-cli", command]
    
    # Convert args dict to CLI arguments
    for key, value in args.items():
        cli_args.append(f"--{key}")
        cli_args.append(str(value))

    logger.info(f"Running command: {' '.join(cli_args)}")
    
    try:
        # Run the command and capture the output
        result = subprocess.run(
            cli_args,
            check=True,
            capture_output=True,
            text=True,
            cwd=root_dir,
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


# Register tools for each TypeSpec client generator CLI command
@mcp.tool("init")
def init_tool(tsp_config_url: str, root_dir: Optional[str] = None) -> Dict[str, Any]:
    """Initialize a typespec client library directory given the url.
    
    Args:
        tsp_config_url: The URL to the tspconfig.yaml file.
        root_dir: The root directory where the client library will be generated.
    
    Returns:
        A dictionary containing the result of the command.
    """
    # Get the URL to the tspconfig.yaml file
    updated_url = get_latest_commit(tsp_config_url)
    
    # Prepare arguments for the CLI command
    args = {}
    args["tsp-config"] = updated_url
    
    return run_typespec_cli_command("init", args, root_dir=root_dir)

# Run the MCP server
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
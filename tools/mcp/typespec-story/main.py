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
        logger.info(f"Extracted repo parts: {repo_parts}")
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
            if os.name == "nt":  # Windows
                result = subprocess.Popen(
                    cli_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,  # Explicitly close stdin
                    text=True,
                    cwd=root_dir,
                )
                result.wait()  # Wait for it to complete
            else:
                result = subprocess.run(
                    cli_args,
                    capture_output=True,
                    text=True,
                    cwd=root_dir,
                )
        else:
            if os.name == "nt":
                result = subprocess.Popen(
                    cli_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,  # Explicitly close stdin
                    text=True
                )
                result.wait()
            result = subprocess.run(
                cli_args,
                capture_output=True,
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
        root_dir: The root directory where the client library will be generated.
    
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
def init_local_tool(tsp_config_path: str) -> Dict[str, Any]:
    """Initializes and subsequently generates a typespec client library directory from a local azure-rest-api-specs repo.

    This command is used to generate a client library from a local azure-rest-api-specs repository. No additional
    commands are needed to generate the client library.


    Args:
        tsp_config_path: The path to the local tspconfig.yaml file.

    Returns:
        A dictionary containing the result of the command.
    """
    # Prepare arguments for the CLI command
    args = {}
    args["tsp-config"] = tsp_config_path
    
    # If root_dir is not provided, use the repository root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    logger.info(f"No root_dir provided, using repository root: {root_dir}")
    
    return run_typespec_cli_command("init", args, root_dir=root_dir)

@mcp.tool("generate")
def generate_tool(project_dir: Optional[str] = None) -> Dict[str, Any]:
    """Generates a typespec client library given the url.
    
    Args:
        project_dir: The directory of the client library to be generated.
    
    Returns:
        A dictionary containing the result of the command.
    """
    # Prepare arguments for the CLI command
    args: Dict[str, Any] = {}
    
    # If project_dir is not provided, use the current directory
    if project_dir is None:
        logger.info("No project_dir provided, using current directory")
    
    return run_typespec_cli_command("generate", args, root_dir=project_dir)

@mcp.tool("update")
def update_tool(project_dir: Optional[str] = None) -> Dict[str, Any]:
    """Updates and generates a typespec client library.
    
    This command looks for a tsp-location.yaml file in the current directory to sync a TypeSpec project
    and generate a client library. It calls sync and generate commands internally.
    
    Args:
        project_dir: The root directory where the client library will be updated.
    
    Returns:
        A dictionary containing the result of the command.
    """
    # Prepare arguments for the CLI command
    args: Dict[str, Any] = {}
    
    # If project_dir is not provided, use the current directory as this command
    # expects to find tsp-location.yaml in the working directory
    if project_dir is None:
        logger.info("No project_dir provided, using current directory")
    
    return run_typespec_cli_command("update", args, root_dir=project_dir)

@mcp.tool("sync") 
def sync_tool(project_dir: Optional[str] = None) -> Dict[str, Any]:
    """Sync a typespec client library from the remote repository.
    This command looks for a tsp-location.yaml file to get the project details and sync them to a temporary directory.
    A generate or update command is then needed to generate the client library.

    Args:
        project_dir: The root directory where the client library will be synced.
    
    Returns:
        A dictionary containing the result of the command.
    """
    # Prepare arguments for the CLI command
    args: Dict[str, Any] = {}
    
    # If project_dir is not provided, use the current directory as this command
    # expects to find tsp-location.yaml in the working directory
    if project_dir is None:
        logger.info("No project_dir provided, using current directory")
    
    return run_typespec_cli_command("sync", args, root_dir=project_dir)

@mcp.tool("sync_local")
def sync_local_tool(local_spec_repo: str, project_dir: Optional[str] = None) -> Dict[str, Any]:
    """Sync a typespec client library from a local repository.

    This command looks for a tsp-location.yaml file to get the project details and sync them to a temporary directory.
    A generate or update command is then needed to generate the client library.
    
    Args:
        local_spec_repo: The path to the local azure-rest-api-specs repository.
        project_dir: The root directory where the client library will be synced.

    Returns:
        A dictionary containing the result of the command.
    """
    # Prepare arguments for the CLI command
    args: Dict[str, Any] = {}
    args["local-spec-repo"] = local_spec_repo
    
    # If project_dir is not provided, use the current directory
    if project_dir is None:
        logger.info("No project_dir provided, using current directory")
    
    return run_typespec_cli_command("sync", args, root_dir=project_dir)

# Run the MCP server
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
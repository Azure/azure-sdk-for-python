import re
from mcp.server.fastmcp import FastMCP
import subprocess
from typing import Dict, Optional, Any
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

def get_latest_commit(tspurl: str) -> str:
    """Get the URL to the tspconfig.yaml file for a given package name from the GitHub repository.
    
    Args:
        package_name: The name of the package to get the latest commit for, e.g. "azure-eventgrid".
        
    Returns:
        The URL to the tspconfig.yaml file for the package in the Azure/azure-rest-api-specs repository.
    """
    # Extract the service name, repo, commit, and tspconfig path from the URL
    # Example URL: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/eventgrid/Azure.Messaging.EventGrid/tspconfig.yaml
    try:
        # Use regex to validate and extract components from the URL
        configUrl = tspurl
        res = re.match(
            r"^https://(?P<urlRoot>github|raw.githubusercontent).com/(?P<repo>[^/]*/azure-rest-api-specs(-pr)?)/(tree/|blob/)?(?P<commit>[0-9a-f]{40})/(?P<path>.*)/tspconfig.yaml$",
            configUrl
        )
        
        if res:
            groups = res.groupdict()
            latest_commit = groups["commit"]
            folder_path = groups["path"]
            # Extract service name from path (usually the second component)
            path_parts = folder_path.split("/")
            service_name = path_parts[1] if len(path_parts) > 1 else "unknown"
            logger.info(f"Using explicit commit from URL: {latest_commit}")
            return latest_commit
        
        # Parse the URL to extract the path within the repository
        repo_parts = tspurl.split("/")
        repo_name = f"{repo_parts[3]}/{repo_parts[4]}"
        
        parts = tspurl.split("azure-rest-api-specs/blob/")[1].split("/")
        parts.pop(0)  # Remove the branch name (e.g., 'main')
        
        # Join all parts until the last directory (containing tspconfig.yaml)
        folder_path = "/".join(parts[:-1])
        logger.info(f"Extracted folder path from URL: {folder_path}")
        
        # Extract service name for logging
        service_name = parts[1] if len(parts) > 1 else "unknown"

        # try:
        auth = Auth.Token(os.getenv("GH_TOKEN"))
        g = Github(auth=auth)
        logger.info(f"Authenticated to GitHub with token: {g}")
        repo = g.get_repo(repo_name)

        # Get commits that affect the specific folder
        commits = repo.get_commits(path=folder_path)

        latest_commit = commits[0].sha
        logger.info(f"Found latest commit for {service_name}: {latest_commit}")
        return latest_commit

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
            # check=True,
            capture_output=True,
            text=True,
            # cwd=root_dir,
        )
        logger.info(f"Command output: {result.stdout}")
        
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {str(e)}")
        return {
            "success": False,
            "stdout": e.stdout,
            "stderr": e.stderr,
            "code": e.returncode,
            "error": str(e)
        }

# Register tools for each TypeSpec client generator CLI command
@mcp.tool("init")
def init_tool(tsp_config_url: str, root_dir: Optional[str] = None) -> Dict[str, Any]:
    """Initialize a typespec client library directory given the package url.
    
    Args:
        tsp_config_url: The URL to the tspconfig.yaml file for the package.
        root_dir: The root directory where the client library will be generated.
    
    Returns:
        A dictionary containing the result of the command.
    """
    # Get the URL to the tspconfig.yaml file
    commit_id = get_latest_commit(tsp_config_url)
    
    # Prepare arguments for the CLI command
    args = {}
    args["tsp-config"] = tsp_config_url
    args["commit"] = commit_id
    
    return run_typespec_cli_command("init", args, root_dir=root_dir)

# @mcp.tool("update")
# def update_tool(path: Optional[str] = None) -> Dict[str, Any]:
#     """Look for a tsp-location.yaml file to sync a TypeSpec project and generate a client library.
    
#     Args:
#         path: Path to a tsp-location.yaml file or a directory containing one.
    
#     Returns:
#         A dictionary containing the result of the command.
#     """
#     args = {}
#     if path:
#         args["_"] = [path]
    
#     return run_typespec_cli_command("update", args)

# @mcp.tool("sync")
# def sync_tool(repo_url: str, commit: Optional[str] = None, tag: Optional[str] = None, 
#               branch: Optional[str] = None, path: Optional[str] = None) -> Dict[str, Any]:
#     """Sync a TypeSpec project with parameters specified in tsp-location.yaml.
    
#     Args:
#         repo_url: URL of the repository containing the TypeSpec project.
#         commit: Commit hash to sync to.
#         tag: Tag to sync to.
#         branch: Branch to sync to.
#         path: Path within the repository to the TypeSpec project.
    
#     Returns:
#         A dictionary containing the result of the command.
#     """
#     args = {
#         "_": [repo_url]
#     }
    
#     if commit:
#         args["commit"] = commit
#     if tag:
#         args["tag"] = tag
#     if branch:
#         args["branch"] = branch
#     if path:
#         args["path"] = path
    
#     return run_typespec_cli_command("sync", args)

# @mcp.tool("generate")
# def generate_tool(project_directory: str, output_directory: Optional[str] = None, 
#                  language: Optional[str] = None, tsp_emit: Optional[str] = None,
#                  service_dir: Optional[str] = None) -> Dict[str, Any]:
#     """Generate a client library from a TypeSpec project.
    
#     Args:
#         project_directory: The directory containing the TypeSpec project.
#         output_directory: The directory where the client library will be generated.
#         language: The language to generate client code for.
#         tsp_emit: The emitter to use for generating the client library.
#         service_dir: The directory containing the service definition.
    
#     Returns:
#         A dictionary containing the result of the command.
#     """
#     args = {
#         "_": [project_directory]
#     }
    
#     if output_directory:
#         args["output-dir"] = output_directory
#     if language:
#         args["language"] = language
#     if tsp_emit:
#         args["tsp-emit"] = tsp_emit
#     if service_dir:
#         args["service-dir"] = service_dir
    
#     return run_typespec_cli_command("generate", args)

# @mcp.tool("convert")
# def convert_tool(swagger_path: str, output_directory: Optional[str] = None, 
#                 title: Optional[str] = None, version: Optional[str] = None) -> Dict[str, Any]:
#     """Convert an existing swagger specification to a TypeSpec project.
    
#     Args:
#         swagger_path: Path to the Swagger specification file.
#         output_directory: The directory where the TypeSpec project will be generated.
#         title: The title for the generated TypeSpec project.
#         version: The version for the generated TypeSpec project.
    
#     Returns:
#         A dictionary containing the result of the command.
#     """
#     args = {
#         "_": [swagger_path]
#     }
    
#     if output_directory:
#         args["output-dir"] = output_directory
#     if title:
#         args["title"] = title
#     if version:
#         args["version"] = version
    
#     return run_typespec_cli_command("convert", args)

# @mcp.tool("compare")
# def compare_tool(old_swagger: str, new_swagger: str, output_file: Optional[str] = None) -> Dict[str, Any]:
#     """Compare two Swagger definitions to identify relevant differences.
    
#     Args:
#         old_swagger: Path to the old Swagger specification file.
#         new_swagger: Path to the new Swagger specification file.
#         output_file: Path to the output file where the comparison results will be written.
    
#     Returns:
#         A dictionary containing the result of the command.
#     """
#     args = {
#         "_": [old_swagger, new_swagger]
#     }
    
#     if output_file:
#         args["output-file"] = output_file
    
#     return run_typespec_cli_command("compare", args)

# @mcp.tool("sort_swagger")
# def sort_swagger_tool(swagger_path: str, output_file: Optional[str] = None) -> Dict[str, Any]:
#     """Sort an existing swagger specification to match TypeSpec generated swagger order.
    
#     Args:
#         swagger_path: Path to the Swagger specification file.
#         output_file: Path to the output file where the sorted Swagger will be written.
    
#     Returns:
#         A dictionary containing the result of the command.
#     """
#     args = {
#         "_": [swagger_path]
#     }
    
#     if output_file:
#         args["output-file"] = output_file
    
#     return run_typespec_cli_command("sort-swagger", args)

# @mcp.tool("generate_config_files")
# def generate_config_files_tool(output_directory: Optional[str] = None) -> Dict[str, Any]:
#     """Generate default configuration files used by tsp-client.
    
#     Args:
#         output_directory: The directory where the configuration files will be generated.
    
#     Returns:
#         A dictionary containing the result of the command.
#     """
#     args = {}
    
#     if output_directory:
#         args["output-dir"] = output_directory
    
#     return run_typespec_cli_command("generate-config-files", args)

# Run the MCP server
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
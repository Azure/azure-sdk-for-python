"""Manage test recording assets with the test-proxy tool.

This command provides a unified interface for managing test recordings
stored in the azure-sdk-assets repository.
"""

import argparse
import os
import sys
import shlex
import subprocess
from pathlib import Path
from typing import Optional, List

from ci_tools.variables import discover_repo_root
from ci_tools.logging import logger

from .Check import Check


class recording(Check):
    """Manage test recording assets via the test-proxy tool.
    
    This command wraps the test-proxy asset sync functionality, providing
    verbs for pushing, restoring, resetting, locating, and showing recording
    assets.
    """

    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `recording` command with subcommands for asset management."""
        parents = parent_parsers or []
        
        # Create main recording parser
        p = subparsers.add_parser(
            "recording",
            parents=parents,
            help="Manage test recording assets",
            description="Manage test recording assets stored in azure-sdk-assets repository",
        )
        
        # Create subparsers for recording verbs
        recording_subparsers = p.add_subparsers(
            title="recording commands",
            dest="recording_verb",
            required=True,
            help="Asset management operations",
        )
        
        # Common argument for assets.json path
        path_arg = argparse.ArgumentParser(add_help=False)
        path_arg.add_argument(
            "-p",
            "--path",
            default="assets.json",
            help='The relative path to your package\'s assets.json file. Default is "assets.json" in current directory.',
        )
        
        # Push command
        push_parser = recording_subparsers.add_parser(
            "push",
            parents=[path_arg],
            help="Push recording updates to a new assets repo tag and update assets.json",
        )
        push_parser.set_defaults(func=self.run)
        
        # Restore command
        restore_parser = recording_subparsers.add_parser(
            "restore",
            parents=[path_arg],
            help="Fetch recordings from the assets repo based on the tag in assets.json",
        )
        restore_parser.set_defaults(func=self.run)
        
        # Reset command
        reset_parser = recording_subparsers.add_parser(
            "reset",
            parents=[path_arg],
            help="Discard any pending changes to recordings based on the tag in assets.json",
        )
        reset_parser.set_defaults(func=self.run)
        
        # Locate command
        locate_parser = recording_subparsers.add_parser(
            "locate",
            parents=[path_arg],
            help="Print the location of the library's locally cached recordings",
        )
        locate_parser.set_defaults(func=self.run)
        
        # Show command
        show_parser = recording_subparsers.add_parser(
            "show",
            parents=[path_arg],
            help="Print the contents of the provided assets.json file",
        )
        show_parser.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Execute the recording management command."""
        
        if not hasattr(args, 'recording_verb') or not args.recording_verb:
            logger.error("No recording verb specified. Use one of: push, restore, reset, locate, show")
            return 1
        
        verb = args.recording_verb
        assets_path = args.path
        
        logger.info(f"Running 'azpysdk recording {verb}' with assets.json path: {assets_path}")
        
        # Normalize path for cross-platform compatibility
        normalized_path = assets_path.replace("\\", "/")
        
        # Get repository root
        try:
            repo_root = self._ascend_to_root(os.getcwd())
            logger.info(f"Repository root: {repo_root}")
        except Exception as e:
            logger.error(f"Failed to find repository root: {e}")
            return 1
        
        # Prepare test-proxy tool
        try:
            tool_name = self._prepare_local_tool(repo_root)
            logger.info(f"Using test-proxy tool: {tool_name}")
        except Exception as e:
            logger.error(f"Failed to prepare test-proxy tool: {e}")
            return 1
        
        # Build command based on verb
        config_commands = {"locate", "show"}
        if verb in config_commands:
            command = f"{tool_name} config {verb.lower()} -a {normalized_path}"
        else:
            command = f"{tool_name} {verb.lower()} -a {normalized_path}"
        
        logger.info(f"Executing command: {command}")
        
        # Execute the command
        try:
            result = subprocess.run(
                shlex.split(command),
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=False,
            )
            
            if result.returncode != 0:
                logger.error(f"Command failed with exit code {result.returncode}")
                return result.returncode
            
            logger.info(f"Successfully completed '{verb}' operation")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return 1

    def _ascend_to_root(self, start_dir: str) -> str:
        """Ascend from start directory until finding a .git folder."""
        from devtools_testutils.proxy_startup import ascend_to_root
        return ascend_to_root(start_dir)
    
    def _prepare_local_tool(self, repo_root: str) -> str:
        """Prepare and return the path to the test-proxy executable."""
        from devtools_testutils.proxy_startup import prepare_local_tool
        return prepare_local_tool(repo_root)

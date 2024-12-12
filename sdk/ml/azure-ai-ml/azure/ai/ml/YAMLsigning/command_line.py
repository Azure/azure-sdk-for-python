# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from abc import ABC, abstractmethod
import base64
import logging
from omegaconf import OmegaConf
from pathlib import Path
import subprocess
import sys
import os
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import asdict

# from shrike import __version__
from configuration import Configuration, load_configuration
# from utils import TelemetryLogger

log = logging.getLogger(__name__)


class _LogEmphasize:
    def __init__(self, line: str):
        self.line = line

    def __enter__(self):
        log.info(self.line)

    def __exit__(self, exc_type, exc_value, traceback):
        log.info(self.line)


class Command(ABC):
    """
    Commands exposed by this package should subclass this class and implement
    the `run_with_config` method. They should be invoked by calling
    `Subclass().run()` inside their module's `__main__` logic.
    """

    @abstractmethod
    def __init__(self) -> None:
        self.config: Configuration = None  # type: ignore
        self._component_statuses: Dict[str, Dict[str, str]] = {}
        self._errors: List[str] = []
        self.nb_cores = 1

    def attach_workspace(self, workspace_id: str = None) -> None: # type: ignore
        """
        Run `az ml folder attach` to the configured workspace ID. Default to the
        first configured workspace if none is provided.
        """
        # self.config.working_directory = "C:\Projects\\azure-sdk-for-python\sdk\ml\\azure-ai-ml\\azure\\ai\ml\YAMLsigning"
        working_direcotry = self.config.working_directory
        if workspace_id is None:
            if not self.config.workspaces and self.config.registries:
                workspace_id = self.config.validation_workspace
                if not workspace_id:
                    self.register_error("No workspaces are configured. If you want to publish to registries only, please specify one workspace string in `validation_workspace` for validating components.")
                    return
            else:
                try:
                    workspace_id = self.config.workspaces[0]
                except IndexError:
                    self.register_error(
                        f"No workspaces are configured. Please include them in your configuration file and ensure the path to your configuration file is correct relative to the working directory {working_direcotry} using `--configuration-file PATH/TO/CONFIGURATION_FILE`."
                    )
                    return

        (subscription_id, resource_group, workspace) = self.parse_workspace_arm_id(
            workspace_id
        )
        success = self.execute_azure_cli_command(
            f"account set --subscription {subscription_id}"
        )
        dir = "C:\Projects\\azure-sdk-for-python\sdk\ml\\azure-ai-ml\\azure\\ai\ml\YAMLsigning"
        print(working_direcotry, dir)
        success = success and self.execute_azure_cli_command(
            f"ml data create --name dataSource --path {dir} --type uri_folder -w {workspace} -g {resource_group}"
            # f"ml folder attach --workspace-name {workspace} --resource-group {resource_group} --debug" # TODO: command modified for v2
        )
        if not success:
            self.register_error(f"Error!! Failed to attach to {workspace_id}!")

    def display_all_statuses(self) -> None:
        """
        Display all component statuses in an easily readable format.
        """
        pass

    def emphasize(self, line: str = "#" * 80) -> _LogEmphasize:
        """
        Use this to initialize a `with` block for emphasizing any logs inside
        that block.
        """
        return _LogEmphasize(line)

    def ensure_component_cli_installed(self) -> bool:
        """
        Check if the component CLI is installed;
        install it if not.
        # TODO get cli version as config.
        """

        # Check whether the component CLI is installed
        component_cli_exists = self.execute_azure_cli_command(
            "extension show -n ml",
            stderr_is_failure=False,
            log_error=False,
        )

        if component_cli_exists:
            log.info("component CLI exists. Skipping installation.")
            return True
        else:
            log.info(
                f"installing component CLI version {self.config.component_cli_version}."
            )
            cli_install_command = f"extension add --name ml"
            # cli_install_command = f"extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/componentsdk/azure_cli_ml-{self.config.component_cli_version}-py3-none-any.whl --pip-extra-index-urls https://azuremlsdktestpypi.azureedge.net/componentsdk/{self.config.component_cli_version} --yes" # TODO: command modified for v2
            if self.config.verbose:
                cli_install_command += " --verbose"

            is_installed = self.execute_azure_cli_command(
                command=cli_install_command,
                # installation may show time to install
                stderr_is_failure=False,
            )

            if is_installed:
                log.info("component CLI is installed.")
            else:
                log.error("component CLI installation failed.")

            return is_installed

    def execute_azure_cli_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        stderr_is_failure: bool = True,
        fail_if_version_exists: bool = False,
        log_error: bool = True,
    ) -> bool:
        """
        Use this method, NOT `execute_command`, for running Azure CLI commands.
        The `command` string should contain everything AFTER the `az`.

        This does NOT use the `azure-cli-core` Python package
        ( https://stackoverflow.com/a/55960725 ) because it takes a long time
        to install, and does not work in Windows.

        This method is necessary for subtle reasons around the way Azure CLI
        exposes commands. The "naive approach" doesn't work.
        """
        log.debug(f"Executing: az {command}")
        az_command_bytes = bytes(f"az {command}", "utf-16le")
        az_command_b64 = base64.b64encode(az_command_bytes).decode("ascii")
        pwsh_command = ["pwsh", "-EncodedCommand", az_command_b64]
        success = self.execute_command(
            pwsh_command, working_dir, stderr_is_failure, fail_if_version_exists, log_error
        )
        return success

    def execute_command(
        self,
        command: List[str],
        working_dir: Optional[str] = None,
        stderr_is_failure: bool = True,
        fail_if_version_exists: bool = False,
        log_error: bool = True,
    ) -> bool:
        """
        Execute the provided shell command using the configured timeout. Working
        directory defaults to the configured one. If `stderr_is_failure` is
        set to false, stderr from the command will be converted to "vanilla"
        logs and will not affect success; 

        Logs are NOT streamed realtime - they are "bundled together" after the
        command executes or times out.

        Warning: running `az *` naively via this function will not work, since
        the Azure CLI is not, by default, discoverable via `subprocess.run`.
        """
        if working_dir is None:
            working_dir = self.config.working_directory

        if len(command) > 0 and command[0] == "az":
            raise ValueError(
                "Do not run Azure CLI commands with this function. Use execute_azure_cli_command instead."
            )

        kwargs = {}

        if stderr_is_failure or fail_if_version_exists:
            kwargs["stderr"] = subprocess.PIPE

        log.debug(f"Executing {command} in {working_dir}")

        timeout = self.config.shell_command_timeout_in_seconds

        try:
            res = subprocess.run(
                args=command,
                cwd=working_dir,
                stdout=subprocess.PIPE,
                timeout=timeout,
                **kwargs,
            )

            success = res.returncode == 0

            if not success:
                if log_error:
                    log.error(f"Command failed with exit code {res.returncode}")
                else:
                    log.info(f"Command failed with exit code {res.returncode}")

            stdout = res.stdout
            stderr = res.stderr
        except subprocess.TimeoutExpired as e:
            log.error(f"Command timed out after {timeout} seconds.")
            success = False
            stdout = e.stdout
            stderr = e.stderr

        if stdout:
            for line in stdout.splitlines():
                try:
                    line = str(line, encoding="utf-8", errors="ignore")  # type: ignore
                except:
                    log.debug(
                        "Failed to convert the following stdout line into String (utf-8)"
                    )
                log.info(line)
        if stderr:
            for line in stderr.splitlines():
                try:
                    line = str(line, encoding="utf-8", errors="ignore")  # type: ignore
                except:
                    log.debug(
                        "Failed to convert the following stdout line into String (utf-8)"
                    )
                if stderr_is_failure:
                    log.error(line)
                    success = False
                elif fail_if_version_exists and "Error" in line and "already exists in" in line: # type: ignore
                    log.error(line)
                    success = False                       
                else:
                    log.info(line)

        return success

    def normalize_path(self, path: Union[str, Path], directory=False) -> str:
        """
        Normalize the provided path (file or directory) to the following format:
        - Absolute (not relative)
        - Linux-style (forward slash separating directories)
        - If `directory=True`, ending in a forward slash.
        """
        if isinstance(path, str):
            path = Path(path)

        path = str(path.absolute())
        rv = path.replace("\\", "/")

        if directory and not rv[-1] == "/":
            rv += "/"

        return rv

    def parse_workspace_arm_id(self, id: str) -> Tuple[str, str, str]:
        """
        Parse a workspace ARM ID like
        `/subscriptions/48bbc269-ce89-4f6f-9a12-c6f91fcb772d/resourceGroups/aml1p-rg/providers/Microsoft.MachineLearningServices/workspaces/aml1p-ml-wus2`
        and return (subscription ID, resource group, workspace name).
        """
        split = id.split("/")
        subscription = split[2]
        resource_group = split[4]
        workspace = split[8]
        return (subscription, resource_group, workspace)

    def register_component_status(
        self, component_name: str, status_name: str, status: str
    ) -> None:
        """
        Register a status (e.g., build = failed) for a specified component. All
        statuses will be displayed in a friendly manner before exiting.
        """
        if component_name not in self._component_statuses:
            self._component_statuses[component_name] = {}

        status_dict = self._component_statuses[component_name]
        status_dict[status_name] = status

    def register_error(self, error: str) -> None:
        """
        Register that an error has occured (also, log it). If any errors have
        been registered, the `run` method will return with non-zero exit code.
        """
        log.error(error)
        self._errors.append(error)

    # def telemetry_logging(self, command: str) -> None:
    #     """
    #     Log the telemetry information in the Azure Application Insights
    #     """
    #     telemetry_logger = TelemetryLogger(
    #         enable_telemetry=not self.config.disable_telemetry
    #     )
    #     telemetry_logger.log_trace(
    #         message=f"shrike.build=={__version__}: {command}",
    #         properties={
    #             "custom_dimensions": {"configuration": str(asdict(self.config))}
    #         },
    #     )

    def run(self) -> None:
        """
        Call this to load the configuration object, initialize the logging tree,
        then invoke the subclass' `run_with_config` method and return the
        appropriate exit code. This should be the entrypoint inside a command's
        `if __name__ == "__main__"` block.
        """
        config = load_configuration()

        log_level = "DEBUG" if config.verbose else "INFO"
        logging.basicConfig(level=log_level, format=config.log_format)
        
        max_nb_cores = max(os.cpu_count() - 1, 1) # type: ignore
        if config.number_of_cores_parallel <= 0 or config.number_of_cores_parallel > max_nb_cores:
            self.nb_cores = max_nb_cores
        else:
            self.nb_cores = config.number_of_cores_parallel

        with self.emphasize():
            config_yaml = OmegaConf.to_yaml(config)
            log.info("Final configuration being used:\n")
            log.info(config_yaml)

        self.config = config
        self.run_with_config()

        self.display_all_statuses()

        failed = bool(self._errors)

        if failed:
            log.error(f"Encountered {len(self._errors)} errors!")

        sys.exit(bool(self._errors))

    @abstractmethod
    def run_with_config(self) -> None:
        """
        Run the subclasses command with the specified configuration object.
        Before this method is invoked, there is no guarantee that `self.config`
        will be populated; after it is invoked, that is guaranteed.
        Implementations of this method should NOT mutate the logging tree in
        any way. They should also NOT raise any exceptions; rather they should
        call the `register_error` method, which will ensure non-zero exit code.
        Implementations can raise specific "status information" (e.g., a
        component is not "active") by calling `register_component_status`.
        """
        pass

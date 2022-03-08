import logging
import os
import pdb
import sys

from .variables import ENV_NAME_REPO_ROOT, FILES_IN_ROOT

RUN_CONFIGURATION_FMT_STRING = """Executable: {executable}.
Repository Root: {root}.
Working Directory: {workdir}.
Logging Level: {log_level}.

"""


class RunConfiguration:
    def __init__(self, root_folder, remaining_args, **kwargs):
        self.log_level = kwargs.get("log_level", logging.INFO)
        self.configure_logging(kwargs)
        self.repo_root = self.resolve_repo_root(root_folder)
        # We will call all commands through RunConfiguration.executable.
        # This will allow for easy override later. Though additional cmd.
        self.executable = sys.executable
        self.invoking_directory = os.getcwd()
        self.set_dev_context()

    def initialize_run(self, customizations={}):
        pass

    def configure_logging(self, args):
        pass

    def set_dev_context(self):
        # this should update the local directories with dev versioning
        pass

    def resolve_repo_root(self, root_folder):
        if os.getenv(ENV_NAME_REPO_ROOT):
            return os.path.abspath(os.getenv(ENV_NAME_REPO_ROOT))

        if root_folder:
            return os.path.abspath(root_folder)
        else:
            current_directory = os.getcwd()

            while current_directory:
                directory_contents = os.listdir(current_directory)

                if all(item in directory_contents for item in FILES_IN_ROOT):
                    return os.path.abspath(current_directory)

                head, _ = os.path.split(current_directory)

                if current_directory == head:
                    print("azci Unable to locate root of repository. Exiting.")
                    exit(1)
                else:
                    current_directory = head

    def __str__(self):
        return RUN_CONFIGURATION_FMT_STRING.format(
            executable=sys.executable, root=self.repo_root, log_level=self.log_level, workdir=self.invoking_directory
        )

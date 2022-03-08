import logging
import os
import pdb

from .variables import ENV_NAME_REPO_ROOT, FILES_IN_ROOT


class RunConfiguration:
    def __init__(self, root_folder, remaining_args, **kwargs):
        self.log_level = kwargs.get("log_level", logging.INFO)
        self.configure_logging(kwargs)
        self.repo_root = self.resolve_repo_root(root_folder)
        pdb.set_trace()
        pass

    def initialize_run(self, customizations={}):
        pass

    def configure_logging(self, args):
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
        return "Implement me!"

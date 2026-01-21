import argparse
import json
import os
import sys

from typing import Optional, List
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.variables import in_ci, set_envvar_defaults
from ci_tools.variables import discover_repo_root
from ci_tools.environment_exclusions import is_check_enabled, is_typing_ignored
from ci_tools.scenario.generation import create_package_and_install

from ci_tools.logging import logger

PYRIGHT_VERSION = "1.1.405"
REPO_ROOT = discover_repo_root()


def get_pyright_config_path(package_dir: str, staging_dir: str) -> str:
    if os.path.exists(os.path.join(package_dir, "pyrightconfig.json")):
        config_path = os.path.join(package_dir, "pyrightconfig.json")
    else:
        config_path = os.path.join(REPO_ROOT, "pyrightconfig.json")

    # read the config and adjust relative paths
    with open(config_path, "r") as f:
        config_text = f.read()
        config_text = config_text.replace('"**', '"../../../../**')
        config = json.loads(config_text)

    # add or update the execution environment
    if config.get("executionEnvironments"):
        config["executionEnvironments"].append({"root": package_dir})
    else:
        config.update({"executionEnvironments": [{"root": package_dir}]})

    pyright_config_path = os.path.join(staging_dir, "pyrightconfig.json")

    with open(pyright_config_path, "w+") as f:
        f.write(json.dumps(config, indent=4))
    return pyright_config_path


class pyright(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the pyright check. The pyright check installs pyright and runs pyright against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser("pyright", parents=parents, help="Run the pyright check")
        p.set_defaults(func=self.run)

        p.add_argument(
            "--next",
            default=False,
            help="Next version of pyright is being tested.",
            required=False,
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the pyright check command."""
        logger.info("Running pyright check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for pyright check")

            try:
                if args.next:
                    # use latest version of pyright
                    install_into_venv(executable, ["pyright"], package_dir)
                else:
                    install_into_venv(executable, [f"pyright=={PYRIGHT_VERSION}"], package_dir)
            except CalledProcessError as e:
                logger.error("Failed to install pyright:", e)
                return e.returncode

            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type="sdist",
                pre_download_disabled=False,
                python_executable=executable,
            )

            self.install_dev_reqs(executable, args, package_dir)

            top_level_module = parsed.namespace.split(".")[0]
            paths = [
                os.path.join(package_dir, top_level_module),
            ]

            if not args.next and in_ci() and not is_check_enabled(package_dir, "pyright"):
                logger.info(
                    f"Package {package_name} opts-out of pyright check. See https://aka.ms/python/typing-guide for information."
                )
                continue
            else:
                # check if samples dir exists, if not, skip sample code check
                samples = os.path.exists(os.path.join(package_dir, "samples"))
                generated_samples = os.path.exists(os.path.join(package_dir, "generated_samples"))
                if not samples and not generated_samples:
                    logger.info(f"Package {package_name} does not have a samples directory.")
                else:
                    paths.append(os.path.join(package_dir, "samples" if samples else "generated_samples"))

            config_path = get_pyright_config_path(package_dir, staging_directory)

            commands = [
                executable,
                "-m",
                "pyright",
                "--project",
                config_path,
            ]
            commands.extend(paths)

            try:
                self.run_venv_command(executable, commands[1:], package_dir, check=True)
                logger.info(f"Pyright check passed for {package_name}.")
            except CalledProcessError as error:
                logger.error("Pyright reported issues:")
                logger.error(error.stdout)
                if (
                    args.next
                    and in_ci()
                    and is_check_enabled(args.target_package, "pyright")
                    and not is_typing_ignored(package_name)
                ):
                    from gh_tools.vnext_issue_creator import create_vnext_issue

                    create_vnext_issue(package_dir, "pyright")

                print("See https://aka.ms/python/typing-guide for information.\n\n")
                results.append(1)

            if args.next and in_ci() and not is_typing_ignored(package_name):
                from gh_tools.vnext_issue_creator import close_vnext_issue

                close_vnext_issue(package_name, "pyright")

        return max(results) if results else 0

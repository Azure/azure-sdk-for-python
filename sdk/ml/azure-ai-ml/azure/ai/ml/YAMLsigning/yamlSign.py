# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
import os
import sys
import multiprocessing
import collections
import jsonpath_ng
import chardet
import re
from typing import List, Set, Union
import shutil
from ruamel.yaml import YAML
from git import Repo, InvalidGitRepositoryError, NoSuchPathError

from command_line import Command
from utils import (
    create_catalog_stub,
    add_file_to_catalog,
    write_two_catalog_files,
    delete_two_catalog_files,
)
from pathlib import Path
import yaml
import urllib.parse
import uuid
from urllib.parse import urlparse
from enum import Enum

log = logging.getLogger(__name__)

ALLOWED_CONTAINER_REGISTRIES = ["polymerprod.azurecr.io"]
ALLOWED_PACKAGE_FEEDS = [
    "https://o365exchange.pkgs.visualstudio.com/_packaging/PolymerPythonPackages/pypi/simple/"
]


class RuntimeEnvironment(Enum):
    AZURE_DEVOPS_BUILD = "Azure DevOps Build"
    GITHUB_ACTION = "GitHub Action"
    OTHER = "Other"


class OperatingSystem(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    OTHER = "Other"


class TargetType(Enum):
    ADDITIONAL_INCLUDES = "additional_includes"
    DEPENDENCY_HINTS = "dependency_hints"


class ActionType(Enum):
    VALIDATE = "validate"
    BUILD = "build"


class Prepare(Command):
    def __init__(self):
        super().__init__()
        self._component_statuses = {}

    def folder_path(self, file: str) -> str:
        """
        Return the normalized path of the directory containing a file.
        """
        return self.normalize_path(Path(file).parent, directory=True)

    def all_files_in_snapshot(self, manifest: str) -> List[str]:
        """
        Return a list of all normalized files in the snapshot. The input
        (`manifest`) is assumed to be some file, whether AML-style component
        spec or Aether-style auto-approval manifest, in the "root" of the
        snapshot.
        """
        folder_path = self.folder_path(manifest)
        log.info("Absolute path for current component is: " + folder_path)

        # Generate a list of all files in this components folder (including subdirectories)
        rv = []

        # Make sure we pick up Linux-style "hidden" files like .amlignore and
        # hidden "directories", as well as hidden files in hidden directories.
        # https://stackoverflow.com/a/65205404
        # https://stackoverflow.com/a/41447012
        for root, _, file_paths in os.walk(folder_path):
            for file in file_paths:
                file_path = os.path.join(root, file)
                normalized_path = self.normalize_path(file_path)
                rv.append(normalized_path)

        return rv
 
    def find_component_specification_files_using_all(self, dir=None) -> List[str]:
        """
        Find all component specification files in the configured working
        directory matching the configured glob. Return the absolute paths
        of these files in the format of a list of string.
        """
        if dir is None:
            dir = self.config.working_directory
        all_spec_yaml_files_absolute_paths = [
            str(p.absolute())
            for p in Path(dir).glob(self.config.component_specification_glob)
        ]

        return all_spec_yaml_files_absolute_paths

    def find_component_specification_files_using_smart(self) -> List[str]:
        """
        This function returns the list of components (as a list of absolute paths) potentially affected by the latest commit.
        """
        log.info(
            "Determining which components are potentially affected by the current change."
        )
        [repo, current_branch, compliant_branch] = self.identify_repo_and_branches()
        modified_files = self.get_modified_files(repo, current_branch, compliant_branch)
        active_components = self.infer_active_components_from_modified_files(
            modified_files
        )
        return active_components

    def identify_repo_and_branches(self):
        """
        This function returns the current repository, along with the name of the current and compliant branches [repo, current_branch, compliant_branch]. Throws if no repo can be found.
        """
        # identify the repository
        curr_path = Path(self.config.working_directory).resolve()
        try:
            repo = Repo(curr_path, search_parent_directories=True)
            log.info("Found a valid repository in " + repo.git_dir)
        except (InvalidGitRepositoryError, NoSuchPathError):
            message = (
                str(curr_path)
                + " or its parents do not contain a valid repo path or cannot be accessed."
            )
            raise Exception(message)
        try:
            current_branch = str(
                repo.head.ref
            )  # when running from our build the repo head is detached so this will throw an exception
        except TypeError:
            current_branch = os.environ.get("BUILD_SOURCEBRANCH") or os.environ.get(
                "GITHUB_REF"
            )
        log.info("The current branch is: '" + str(current_branch) + "'.")
        # Identify the compliant branch
        if not (self.config.compliant_branch.startswith("^refs/heads/")) or not (
            self.config.compliant_branch.endswith("$")
        ):
            raise Exception(
                "The name of the compliant branch found in the config file should start with '^refs/heads/' and end with '$'. Currently it is: '"
                + self.config.compliant_branch
                + "'."
            )
        else:
            compliant_branch = self.config.compliant_branch.replace("^refs/heads/", "")[
                0:-1
            ]
        log.info("The compliant branch is: '" + compliant_branch + "'.")
        return [repo, current_branch, compliant_branch]

    def get_modified_files(self, repo, current_branch, compliant_branch) -> Set[str]:
        """
        This function returns the paths of files that have been modified. 3 scenarios are supported.\n
        1/ 'Build - before Merge'; when the 'prepare' command is run as part of a build, but before the actual merge (in this case, the name of the current branch starts with 'refs/pull/' - this is the default Azure DevOps behavior).\n
        2/ 'Build - after Merge'; when the 'prepare' command is run as part of a build, after the actual merge (in this case, the name of the current branch is the same as the name of the compliant branch).\n
        3/ 'Manual'; when the prepare command is run manually (typically before publishing the PR).
        """
        # identify the 2 relevant commits based on the use case
        current_commit, previous_commit = self.get_relevant_commits(
            repo, current_branch, compliant_branch
        )

        # take the actual diff
        diff = self.get_diff_between_commits(current_commit, previous_commit)

        # process the diff object to obtain a list of paths
        res = self.extract_paths_from_diff(
            diff,
            repo_working_dir=repo.working_dir,
            repo_working_tree_dir=repo.working_tree_dir,
            repo_git_dir=repo.git_dir,
        )
        return res

    def extract_paths_from_diff(
        self, diff, repo_working_dir, repo_working_tree_dir, repo_git_dir
    ):
        """Function that extracts the paths of the modified files from the diff between 2 commits."""
        res = set()
        # let's build a set with the paths of modified files found in the diff object
        log.debug("Working directory: " + self.config.working_directory)
        log.debug("repo.working_dir: " + repo_working_dir)
        log.debug("repo.working_tree_dir: " + repo_working_tree_dir)
        log.debug("repo.git_dir: " + repo_git_dir)
        for d in diff:
            log.debug("d.a_path: " + d.a_path)
            log.debug("Path(d.a_path).absolute(): " + str(Path(d.a_path).absolute()))
            log.debug("Path(d.a_path).resolve(): " + str(Path(d.a_path).resolve()))
            r_a = str(Path(repo_git_dir).parent / Path(d.a_path))
            res.add(r_a)
            r_b = str(Path(repo_git_dir).parent / Path(d.b_path))
            res.add(r_b)
        log.info("The list of modified files is:")
        log.info(res)
        return res

    def get_relevant_commits(self, repo, current_branch, compliant_branch):
        """
        This function returns the commits required to compute the list of files that have been modified. 3 scenarios are supported.\n
        1/ 'Build - before Merge'; when the 'prepare' command is run as part of a build, but before the actual merge (in this case, the name of the current branch starts with 'refs/pull/' - this is the default Azure DevOps behavior).\n
        2/ 'Build - after Merge'; when the 'prepare' command is run as part of a build, after the actual merge (in this case, the name of the current branch is the same as the name of the compliant branch).\n
        3/ 'Manual'; when the prepare command is run manually (typically before publishing the PR).
        """
        # Grab the diff differently depending on the scenario
        if current_branch.replace("refs/heads/", "") == compliant_branch:
            # 'Build - after Merge' case: we will take the diff between the
            # tree of the latest commit to the compliant branch, and the tree
            # of the previous commit to the compliant branch corresponding to a
            # PR (we assume the commit summary starts with 'Merged PR')
            log.info(
                "We are in the 'Build - after Merge' case (the current branch is the compliant branch)."
            )
            current_commit = self.get_compliant_commit_corresponding_to_pull_request(
                repo, compliant_branch
            )
            self.log_commit_info(current_commit, "Current commit to compliant branch")
            previous_commit = (
                self.get_previous_compliant_commit_corresponding_to_pull_request(
                    current_commit,
                    consider_current_commit=False,
                )
            )
            self.log_commit_info(
                previous_commit, "Previous PR commit to compliant branch"
            )
        elif current_branch.startswith("refs/pull/"):
            # 'Build - before Merge': we will take the diff between the tree of
            # the current commit, and the tree of the previous commit to the
            # compliant branch corresponding to a PR (we assume the commit
            # summary starts with 'Merged PR')
            log.info(
                "We are in the 'Build - before Merge' case (the current branch is not the compliant branch and its name starts with 'refs/pull/')."
            )
            current_commit = repo.commit()
            self.log_commit_info(current_commit, "Current commit to current branch")
            latest_commit_to_compliant_branch = repo.remotes.origin.refs[
                compliant_branch
            ].commit
            previous_commit = (
                self.get_previous_compliant_commit_corresponding_to_pull_request(
                    latest_commit_to_compliant_branch,
                    consider_current_commit=True,
                )
            )
            self.log_commit_info(
                previous_commit, "Previous PR commit to compliant branch"
            )
        else:
            # 'Manual' Case: we will take the diff between the current branch
            # and the compliant branch (we're assuming the compliant branch is
            # locally up to date here)
            log.info(
                "We are in the 'Manual' case (the current branch is NOT the compliant branch and its name does not start with 'refs/pull/')."
            )
            try:
                current_commit = repo.heads[
                    current_branch
                ].commit  # this won't work when running the Manual case from the DevOps portal, but the below will
            except (IndexError, AttributeError):
                current_commit = repo.commit()
            self.log_commit_info(current_commit, "Current commit to current branch")
            try:
                previous_commit = repo.heads[
                    compliant_branch
                ].commit  # this won't work when running the Manual case from the DevOps portal, but the below will
            except (IndexError, AttributeError):
                latest_commit_to_compliant_branch = repo.remotes.origin.refs[
                    compliant_branch
                ].commit
                previous_commit = (
                    self.get_previous_compliant_commit_corresponding_to_pull_request(
                        latest_commit_to_compliant_branch,
                        consider_current_commit=True,
                    )
                )
            self.log_commit_info(previous_commit, "Previous commit to compliant branch")

        return current_commit, previous_commit

    def get_diff_between_commits(self, current_commit, previous_commit):
        """Function that gets the diff between 2 commits."""
        # just use the 'diff' function from gitpython
        return current_commit.tree.diff(previous_commit.tree)

    def log_commit_info(self, commit, title) -> None:
        log.info(title + ":")
        log.info("Summary: " + commit.summary)
        log.info("Author: " + str(commit.author))
        log.info("Authored Date: " + str(commit.authored_date))

    def get_previous_compliant_commit_corresponding_to_pull_request(
        self, latest_commit, consider_current_commit
    ):
        """
        This function will return the previous commit in the repo corresponding to a PR (i.e. that starts with "Merged PR").
        If `consider_current_commit` is set to True, the `latest_commit` will be considered. If set to false, only previous commits will be considered.
        """
        target_string = "Merged PR"
        if consider_current_commit and latest_commit.summary.startswith(target_string):
            return latest_commit
        previous_commit = latest_commit
        for c in previous_commit.iter_parents():
            if c.summary.startswith(target_string):
                previous_commit = c
                break
        return previous_commit

    def get_compliant_commit_corresponding_to_pull_request(
        self, repo, compliant_branch
    ):
        """
        This function will return the most recent commit in the repo that truly corresponds to the triggered build. It is identified thanks to the 'Build.SourceVersionMessage' DevOps environment variable (see https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml) that contains the true commit message. This is used to address the race condition occurring when a commit sneaks in before the "prepare" step was run on the previous commit.
        """
        # this is the true commit message corresponding to the PR that triggered the build
        true_commit_message = self.get_true_commit_message()
        # this is the most recent commit
        current_commit = repo.remotes.origin.refs[compliant_branch].commit
        # if the most recent commit corresponds to the true commit message, then return it
        if true_commit_message.startswith(current_commit.summary):
            return current_commit
        # otherwise, let's iterate through the parents until we find it
        candidate_commit = current_commit
        for c in candidate_commit.iter_parents():
            if true_commit_message.startswith(c.summary):
                return c
        # if the corresponding commit cannot be found, return the most recent one and log a warning
        log.warning(
            "Could not find in the git repo the commit that triggered this PR. Returning the most recent but beware, the 'smart' mode likely will not work properly."
        )
        return current_commit

    def get_true_commit_message(self):
        return str(os.environ.get("BUILD_SOURCEVERSIONMESSAGE") or "NA")

    def infer_active_components_from_modified_files(self, modified_files) -> List[str]:
        """
        This function returns the list of components (as a list of directories paths) potentially affected by changes in the `modified_files`.
        """
        rv = []
        # We will go over components one by one
        all_components_in_repo = self.find_component_specification_files_using_all()
        log.info("List of all components in repo:")
        log.info(all_components_in_repo)
        for component in all_components_in_repo:
            if self.component_is_active(component, modified_files):
                rv.append(component)
        # No need to dedup rv since we are only considering components once
        log.info("The active components are:")
        log.info(rv)
        return rv

    def component_is_active(self, component, modified_files) -> bool:
        """
        This function returns True if any of the 'modified_files' potentially affects the 'component' (i.e. if it is directly in one of the 'component' subfolders, or if it is covered by the additional_includes files). If the component has been deleted, returns False.
        """
        log.info("Assessing whether component '" + component + "' is active...")
        # Let's first take care of the case where the component has been deleted
        if not (Path(component).exists()):
            return False
        # Let's grab the contents of the additional_includes file if it exists.
        component_additional_includes_contents = self.get_target_file_contents(
            component,
            TargetType.ADDITIONAL_INCLUDES,
        )
        # Let's grab the contents of the additional_includes file if it exists.
        component_dependency_hints_contents = self.get_target_file_contents(
            component,
            TargetType.DEPENDENCY_HINTS,
        )
        # loop over all modified files; if current file is in subfolder of component or covered by
        # additional includes or dependency hints, return True
        for modified_file in modified_files:
            if (
                self.is_in_subfolder(modified_file, component)
                or self.is_in_target_list(
                    modified_file,
                    TargetType.ADDITIONAL_INCLUDES,
                    component_additional_includes_contents,
                )
                or self.is_in_target_list(
                    modified_file,
                    TargetType.DEPENDENCY_HINTS,
                    component_dependency_hints_contents,
                )
            ):
                return True
        return False

    def get_target_file_contents(
        self, component, target_type
    ) -> Union[List[str], None]:
        component_target_file_contents = None
        # for depependency hints, we look globally first
        if target_type == TargetType.DEPENDENCY_HINTS:
            component_target_file_contents = self.get_global_dependency_hints_contents(
                component
            )
        # First we figure out the expected path of the additional_includes file
        component_target_file_path = self.get_theoretical_target_file_path(
            component, target_type
        )
        # And we load it if it exists.
        if Path(component_target_file_path).exists():
            rbfile = open(component_target_file_path, "rb").read()
            if chardet.detect(rbfile).get("encoding").lower() not in ["utf-8", "ascii"]: #type: ignore
                raise ValueError(
                    f"Encoding of a file: '{{spec_file_name}}.{target_type.value}' not supported, use UTF-8."
                )

            with open(component_target_file_path, "r") as component_target_file:
                if (target_type == TargetType.DEPENDENCY_HINTS) and (
                    component_target_file_contents is not None
                ):
                    component_target_file_contents += component_target_file.readlines()
                else:
                    component_target_file_contents = component_target_file.readlines()
        else:
            # If additional_includes doesn't exist we log a message explaining the expected name format
            if target_type == TargetType.ADDITIONAL_INCLUDES:
                log.info(
                    "No additional_includes file could be found for the component '"
                    + component
                    + "'. If you tried to create such a file, remember it should live next to the component spec file and should be named '{spec_file_name}.additional_includes'. "
                    + "For example, if the component spec file is named 'component_spec.yaml', the additional_includes file should be named 'component_spec.additional_includes'. In this specific case, the expected additional_includes file name is: '"
                    + component_target_file_path
                    + "'."
                )
                # Then we check whether there is an improperly named additional_includes file in the component folder, and if so we throw
                if self.check_for_wrongly_named_additional_includes(component):
                    raise ValueError(
                        "An additional_includes file which does not respect the naming pattern was found. Please rename this file. Remember it should live next to the component spec file and should be named '{spec_file_name}.additional_includes'."
                        + "For example, if the component spec file is named 'component_spec.yaml', the additional_includes file should be named 'component_spec.additional_includes'."
                    )
        # Before returning, we make the paths in the additional_includes file absolute
        if component_target_file_contents:
            for line_number in range(0, len(component_target_file_contents)):
                component_target_file_contents[line_number] = str(
                    Path(
                        os.path.join(
                            Path(component).parent,
                            component_target_file_contents[line_number].rstrip("\n"),
                        )
                    ).resolve()
                )
        return component_target_file_contents

    def get_global_dependency_hints_contents(self, component) -> Union[List[str], None]:
        if len(self.config.dependency_hints) > 0:
            global_dependency_hints_contents = []
            for (
                component_folder_paths,
                dependency_hints_paths,
            ) in self.config.dependency_hints.items():
                component_folder_absolute_paths = [
                    str(p.absolute().resolve())
                    for p in Path(self.config.working_directory).glob(
                        component_folder_paths
                    )
                ]
                if (
                    str(Path(component).parent.resolve())
                    in component_folder_absolute_paths
                ):
                    if not isinstance(dependency_hints_paths, list):
                        dependency_hints_paths = [dependency_hints_paths]
                    for dependency_hints_path in list(dependency_hints_paths):
                        global_dependency_hints_contents += [
                            str(p.absolute().resolve())
                            for p in Path(self.config.working_directory).glob(
                                dependency_hints_path
                            )
                        ]
            if len(global_dependency_hints_contents) > 0:
                return global_dependency_hints_contents
            else:
                return None
        else:
            return None

    def get_theoretical_target_file_path(self, component, target_type) -> str:
        """
        Returns the expected path of the 'target_type' file
        associated with the 'component'.
        """
        # First, we figure out the name of the target file, based on the component name
        component_name_without_extension = Path(component).name.split(".yaml")[0]
        # Then, we construct the expected path of the target file (see
        # https://componentsdk.azurewebsites.net/components/component-spec-topics/additional-includes.html
        # for the 'additional_includes' case)
        component_target_file_path = os.path.join(
            Path(component).parent,
            component_name_without_extension + "." + str(target_type.value),
        )
        return component_target_file_path

    def check_for_wrongly_named_additional_includes(self, component) -> bool:
        """
        Returns True if the component folder contains an improperly named additional_includes file
        i.e. a lonely additional_includes file without a corresponding spec.yaml
        """
        # grab all potential additional_includes files in the component folder
        potentially_wrongly_named_files = Path(component).parent.glob(
            "*.additional_includes*"
        )
        for potentially_wrongly_named_file in potentially_wrongly_named_files:
            # determine the expected location of the spec
            theoretical_component_path = (
                str(potentially_wrongly_named_file)[:-20] + ".yaml"
            )
            # check if spec exists
            if os.path.isfile(theoretical_component_path):
                continue
            else:
                # if not, we have a problem
                self.register_error(
                    f"Component folder {component} contains a lonely additional includes file at {potentially_wrongly_named_file}, missing component spec {theoretical_component_path}"
                )
                return True
        return False

    def is_in_subfolder(self, modified_file, component) -> bool:
        """
        This function returns True if 'modified_file' is in a subfolder of 'component' ('component' can be either the path to a file, or a directory). If the component has been deleted, returns False.
        """
        # Let's first take care of the case where the component has been deleted
        if not (Path(component).exists()):
            log.debug("'" + component + "' does not exist, returning False.")
            return False
        # Case where the component has not been deleted
        for parent in Path(modified_file).parents:
            if parent.exists():
                if Path(component).is_dir():
                    if parent.samefile(Path(component)):
                        log.info(
                            "'"
                            + modified_file
                            + " is in a subfolder of '"
                            + component
                            + "'."
                        )
                        return True
                else:
                    if parent.samefile(Path(component).parent):
                        log.info(
                            "'"
                            + modified_file
                            + " is in a subfolder of '"
                            + component
                            + "'."
                        )
                        return True
        log.debug(
            "'" + modified_file + " is NOT in a subfolder of '" + component + "'."
        )
        return False

    def is_in_target_list(
        self, modified_file, target_type, target_list_contents
    ) -> bool:
        """
        This function returns True if 'modified_file' is covered by the file
        'target_list_contents'. The 'target_type' can be either
        additional_includes or dependency_hints
        """
        # first tackle the trivial case of no target file
        if target_list_contents is None:
            log.debug(
                f"The component's target file ({target_type}) is empty, returning False."
            )
            return False
        # now the regular scenario
        for line in target_list_contents:
            # when the line from the target list is a file, we directly check its path against that of modified_file
            if Path(line).is_file():
                if str(Path(modified_file).resolve()) == str(
                    Path(line).resolve()
                ):  # can't use 'samefile' here because modified_file is not guaranteed to exist, we resolve the path and do basic == test
                    log.info(
                        "'"
                        + modified_file
                        + f" is directly listed in the {target_type} file."
                    )
                    return True
            # slightly more complicated case: when the line
            # in the target list is a directory, we can just
            # call the is_in_subfolder function
            # but first, we take care of the zipped folders
            if target_type == TargetType.ADDITIONAL_INCLUDES:
                if self.config.detect_changes_in_unzipped_folder:
                    split_line = os.path.splitext(line)
                    if split_line[1] == ".zip":
                        line = split_line[0]
            if Path(line).is_dir():
                if self.is_in_subfolder(modified_file, line):
                    log.info(
                        "'"
                        + modified_file
                        + f" is in one of the directories listed in the {target_type} file."
                    )
                    return True
        log.debug(
            "'"
            + modified_file
            + f" is NOT referenced by the {target_type} file (neither directly nor indirectly)."
        )
        return False


    def find_component_specification_files(self) -> List[str]:
        """
        Find the list of "active" component specification files using the
        configured method ("all" or "smart").
        """
        activation_method = self.config.activation_method

        if activation_method == "all":
            rv = self.find_component_specification_files_using_all()
        elif activation_method == "smart":
            rv = self.find_component_specification_files_using_smart()
        else:
            raise ValueError(
                f"Invalid activation_method provided: '{activation_method}'"
            )

        return rv

    def _create_dependencies_files(self, component_files) -> str:
        id = str(uuid.uuid4())
        path_to_dependencies_files = os.path.join(
            self.config.working_directory, "component_dependencies_" + id
        )
        log.info(
            f"Writing Python package dependencies to path {path_to_dependencies_files}"
        )
        os.makedirs(path_to_dependencies_files)
        for component in component_files:
            self._create_dependencies_files_for_single_component(
                component, path_to_dependencies_files
            )
        return id

    def _create_dependencies_files_for_single_component(
        self, component, path_to_dependencies_files
    ) -> None:
        component_repo = Path(component).parent
        with open(component, "r") as spec_file:
            spec = YAML(typ="safe").load(spec_file)
        (
            pip_dependencies,
            conda_dependencies,
            _,
        ) = self._extract_dependencies_and_channels(component)

        if pip_dependencies or conda_dependencies:
            component_name = spec.get("name")
            cur_path = os.path.join(path_to_dependencies_files, component_name)
            try:
                os.makedirs(cur_path)
            except FileExistsError:
                suffix = (
                    component_name
                    + "_"
                    + os.path.splitext(os.path.basename(component))[0]
                )
                cur_path = os.path.join(path_to_dependencies_files, suffix)
                os.makedirs(cur_path)
            if pip_dependencies:
                log.info(
                    f"Found pip dependencies for component {component_name} in {component_repo}. Writing to requirements.txt."
                )
                with open(os.path.join(cur_path, "requirements.txt"), "w") as file:
                    for req in pip_dependencies:
                        file.write(req)
                        if not req.endswith("\n"):
                            file.write("\n")
            if conda_dependencies:
                log.info(
                    f"Found conda dependencies for component {component_name} in {component_repo}. Writing to environment.yml."
                )
                with open(os.path.join(cur_path, "environment.yml"), "w") as file:
                    yaml.dump(conda_dependencies, file)

    def _extract_dependencies_and_channels(self, component) -> List[list]:
        component_repo = Path(component).parent
        build_folder = os.path.join(component_repo, ".build")
        if os.path.exists(build_folder):
            component_repo = build_folder
        with open(component, "r") as spec_file:
            spec = YAML(typ="safe").load(spec_file)
        pip_dependencies = []
        conda_dependencies = []
        conda_channels = []
        if "environment" in spec:
            spec_environment = spec.get("environment")
            if "conda" in spec_environment:
                spec_conda = spec_environment["conda"]
                if "conda_dependencies" in spec_conda:
                    conda_dependencies = spec_conda["conda_dependencies"]
                    pip_dependencies += self._extract_python_package_dependencies(
                        conda_dependencies
                    )
                    if "channels" in conda_dependencies:
                        conda_channels += conda_dependencies["channels"]
                if "conda_dependencies_file" in spec_conda:
                    conda_dependencies_file = spec_conda["conda_dependencies_file"]
                    try:
                        with open(
                            os.path.join(
                                component_repo, spec_conda["conda_dependencies_file"]
                            )
                        ) as file:
                            conda_dependencies = YAML(typ="safe").load(file)
                        pip_dependencies += self._extract_python_package_dependencies(
                            conda_dependencies
                        )
                        if "channels" in conda_dependencies:
                            conda_channels += conda_dependencies["channels"]
                    except FileNotFoundError:
                        self.register_error(
                            f"The required conda_dependencies_file {conda_dependencies_file} does not exist in {component_repo}."
                        )
                if "pip_requirements_file" in spec_conda:
                    pip_requirements_file = spec_conda["pip_requirements_file"]
                    try:
                        with open(
                            os.path.join(
                                component_repo, spec_conda["pip_requirements_file"]
                            )
                        ) as file:
                            pip_dependencies += file.readlines()
                    except FileNotFoundError:
                        self.register_error(
                            f"The required pip_requirements_file {pip_requirements_file} does not exist in {component_repo}."
                        )
        return [pip_dependencies, conda_dependencies, conda_channels]

    def _extract_python_package_dependencies(self, conda_dependencies) -> List[str]:
        pip_dependencies = []
        if "dependencies" in conda_dependencies:
            dependencies = conda_dependencies.get("dependencies")
            for dependencies_item in dependencies:
                if isinstance(dependencies_item, dict) and "pip" in dependencies_item:
                    pip_dependencies = dependencies_item["pip"]
        return pip_dependencies

    def create_catalog_files(self, files: List[str]) -> None:
        """
        Create AML-friendly catalog.json and catalog.json.sig files, using
        SHA-256 hash.
        """

        # For each component spec file in the input list, we'll do the following...
        for f in files:
            log.info(f"Processing file {f}")
            component_folder_path = self.folder_path(f)

            # remove catalog files if already present
            log.info("Deleting old catalog files if present")
            delete_two_catalog_files(component_folder_path)

            files_for_catalog = self.all_files_in_snapshot(f)
            log.info("The following list of files will be added to the catalog.")
            log.info(files_for_catalog)

            # Prepare the catlog stub: {'HashAlgorithm': 'SHA256', 'CatalogItems': {}}
            catalog = create_catalog_stub()

            # Add an entry to the catalog for each file
            for file_for_catalog in files_for_catalog:
                catalog = add_file_to_catalog(
                    file_for_catalog, catalog, component_folder_path
                )

            # order the CatalogItems dictionary
            catalog["CatalogItems"] = collections.OrderedDict(
                sorted(catalog["CatalogItems"].items())
            )

            # Write the 2 catalog files
            log.info(catalog)
            write_two_catalog_files(catalog, component_folder_path)
            log.info("Finished creating catalog files.")

    def run_with_config(self):
        log.info("Running component preparation logic.")


        component_files = self.find_component_specification_files()
         
        self.ensure_component_cli_installed()
        self.attach_workspace()
        
        self.create_catalog_files(component_files)
        
        self._create_dependencies_files(component_files)

    def validate_each_components(self, component) -> None:
        """
        For one of component specification file, run `az ml component validate`,
        run compliance and customized validation if enabled,
        and register the status (+ register error if validation failed).
        """
        validate_component_success = self.execute_azure_cli_command(
            f"ml component validate --file {component}"
        )
        compliance_validation_success = True
        customized_validation_success = True
        if self.config.enable_component_validation:
            log.info(f"Running compliance validation on {component}")
            compliance_validation_success = self.compliance_validation(component)
            if len(self.config.component_validation) > 0:
                log.info(f"Running customized validation on {component}")
                for jsonpath, regex in self.config.component_validation.items():
                    customized_validation_success = (
                        customized_validation_success
                        if self.customized_validation(
                            jsonpath,
                            regex,
                            component,
                            self.config.fail_if_pattern_not_found_in_component_validation,
                        )
                        else False
                    )

        if (
            validate_component_success
            and compliance_validation_success
            and customized_validation_success
        ):
            # If the az ml validation succeeds, we continue to check whether
            # the "code" snapshot parameter is specified in the spec file
            # https://componentsdk.z22.web.core.windows.net/components/component-spec-topics/code-snapshot.html
            with open(component, "r") as spec_file:
                spec = YAML(typ="safe").load(spec_file)
            spec_code = spec.get("code")
            if spec_code and spec_code not in [".", "./"]:
                self.register_component_status(component, "validate", "failed")
                self.register_error(
                    "Code snapshot parameter is not supported. Please use .additional_includes for your component."
                )
            else:
                log.info(f"Component {component} is valid.")
                self.register_component_status(component, "validate", "succeeded")
        else:
            self.register_component_status(component, "validate", "failed")
            self.register_error(f"Error when validating component {component}.")

    def compliance_validation(self, component: str) -> bool:
        """
        This function checks whether a given component spec YAML file
        meets all the requirements for running in the compliant AML.
        Specifically, it checks (1) whether the image URL is compliant；
        （2）whether the pip index-url is compliant; (3) whether
        "default" is only Conda channel
        """
        with open(component, "r") as spec_file:
            spec = YAML(typ="safe").load(spec_file)

        # Check whether the docker image URL is compliant
        image_url = jsonpath_ng.parse("$.environment.docker.image").find(spec)
        if len(image_url) > 0:
            if (
                urlparse(image_url[0].value).path.split("/")[0]
                not in ALLOWED_CONTAINER_REGISTRIES
            ):
                log.error(
                    f"The container base image in {component} is not allowed for compliant run."
                )
                return False

        # check whether the package feed is compliant
        (
            package_dependencies,
            conda_dependencies,
            conda_channels,
        ) = self._extract_dependencies_and_channels(component=component)
        if len(package_dependencies) > 0:
            for dependency in package_dependencies:
                if re.match("^--index-url", dependency) or re.match(
                    "^--extra-index-url", dependency
                ):
                    if dependency.split(" ")[1] not in ALLOWED_PACKAGE_FEEDS:
                        log.error(
                            f"The package feed in {component} is not allowed for compliant run."
                        )
                        return False
            if (
                f"--index-url {ALLOWED_PACKAGE_FEEDS[0]}" not in package_dependencies
                and f"--extra-index-url {ALLOWED_PACKAGE_FEEDS[0]}"
                not in package_dependencies
            ):
                log.error(
                    f"The Polymer package feed is not found in environment of {component}"
                )
                return False

        # Check whether "default" is only Conda channel
        if len(conda_channels) > 1 or (
            len(conda_channels) == 1 and conda_channels[0] != "."
        ):
            log.error("Only the default conda channel is allowed for compliant run.")
            return False

        return True

    @staticmethod
    def customized_validation(
        jsonpath: str,
        regex: str,
        component: str,
        fail_if_pattern_not_found_in_component_validation: bool,
    ) -> bool:
        """
        This function leverages regular expressionm atching and
        JSONPath expression to enforce user-provided "strict"
        validation on Azure ML components
        """
        with open(component, "r") as spec_file:
            spec = YAML(typ="safe").load(spec_file)

        parsed_patterns = jsonpath_ng.parse(jsonpath).find(spec)
        validation_success = True
        if not parsed_patterns:
            log.warning(f"The pattern {jsonpath} is not found in {component}")
            if fail_if_pattern_not_found_in_component_validation:
                validation_success = False
        if len(parsed_patterns) > 0:
            for parsed_pattern in parsed_patterns:
                if not re.match(regex, parsed_pattern.value):
                    log.error(
                        f"The parsed pattern {parsed_pattern} in {component} doesn't match the regular expression {regex}"
                    )
                    validation_success = False
        return validation_success


if __name__ == "__main__":
    Prepare().run()

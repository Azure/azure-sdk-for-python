"""Swagger to SDK"""
import os
import shutil
import logging
import json
from pathlib import Path
import tempfile

from git import Repo, GitCommandError

from .SwaggerToSdkCore import (
    read_config_from_github,
    DEFAULT_COMMIT_MESSAGE,
    get_input_paths,
    extract_conf_from_readmes,
    get_readme_files_from_git_object,
    build_file_content,
    solve_relative_path,
    this_conf_will_generate_for_this_pr,
)
from .autorest_tools import (
    execute_simple_command,
    generate_code,
    merge_options,
)
from azure_devtools.ci_tools.git_tools import (
    checkout_and_create_branch,
    do_commit,
)
from azure_devtools.ci_tools.github_tools import (
    configure_user,
    manage_git_folder,
)


_LOGGER = logging.getLogger(__name__)


def move_wrapper_files_or_dirs(src_root, dst_root, global_conf, local_conf):
    """Save wrapper files somewhere for replace them after generation."""
    src_relative_path = local_conf.get("output_dir", "")
    src_abs_path = Path(src_root, src_relative_path)
    dst_abs_path = Path(dst_root, src_relative_path)

    wrapper_files_or_dirs = merge_options(global_conf, local_conf, "wrapper_filesOrDirs") or []

    for wrapper_file_or_dir in wrapper_files_or_dirs:
        for file_path in src_abs_path.glob(wrapper_file_or_dir):
            relative_file_path = file_path.relative_to(src_abs_path)
            file_path_dest = Path(dst_abs_path, relative_file_path)
            if file_path.is_file():
                file_path_dest.parent.mkdir(parents=True, exist_ok=True)
            _LOGGER.info("Moving %s to %s", str(file_path), str(file_path_dest))
            # This does not work in Windows if generatd and dest are not in the same drive
            # file_path.replace(file_path_dest)
            shutil.move(file_path, file_path_dest)


def delete_extra_files(sdk_root, global_conf, local_conf):
    src_relative_path = local_conf.get("output_dir", "")
    src_abs_path = Path(sdk_root, src_relative_path)

    delete_files_or_dirs = merge_options(global_conf, local_conf, "delete_filesOrDirs") or []

    for delete_file_or_dir in delete_files_or_dirs:
        for file_path in src_abs_path.glob(delete_file_or_dir):
            if file_path.is_file():
                file_path.unlink()
            else:
                shutil.rmtree(str(file_path))


def move_autorest_files(client_generated_path, sdk_root, global_conf, local_conf):
    """Update data from generated to final folder.

    This is one only if output_dir is set, otherwise it's considered generated in place
    and does not required moving
    """
    dest = local_conf.get("output_dir", None)
    if not dest:
        return
    destination_folder = get_local_path_dir(sdk_root, dest)

    generated_relative_base_directory = local_conf.get("generated_relative_base_directory") or global_conf.get(
        "generated_relative_base_directory"
    )

    if generated_relative_base_directory:
        client_possible_path = [
            elt for elt in client_generated_path.glob(generated_relative_base_directory) if elt.is_dir()
        ]
        try:
            client_generated_path = client_possible_path.pop()
        except IndexError:
            err_msg = "Incorrect generated_relative_base_directory folder: {}\n".format(
                generated_relative_base_directory
            )
            err_msg += "Base folders were: : {}\n".format(
                [f.relative_to(client_generated_path) for f in client_generated_path.iterdir()]
            )
            _LOGGER.critical(err_msg)
            raise ValueError(err_msg)
        if client_possible_path:
            err_msg = "generated_relative_base_directory parameter is ambiguous: {} {}".format(
                client_generated_path, client_possible_path
            )
            _LOGGER.critical(err_msg)
            raise ValueError(err_msg)

    shutil.rmtree(str(destination_folder))
    # This does not work in Windows if generatd and dest are not in the same drive
    # client_generated_path.replace(destination_folder)
    shutil.move(client_generated_path, destination_folder)


def write_build_file(sdk_root, local_conf):
    build_dir = local_conf.get("build_dir")
    if build_dir:
        build_folder = get_local_path_dir(sdk_root, build_dir)
        build_file = Path(build_folder, "build.json")
        with open(build_file, "w") as build_fd:
            json.dump(build_file_content(), build_fd, indent=2)


def execute_after_script(sdk_root, global_conf, local_conf):
    after_scripts = merge_options(global_conf, local_conf, "after_scripts", keep_list_order=True) or []
    local_envs = dict(os.environ)
    local_envs.update(global_conf.get("envs", {}))

    for script in after_scripts:
        _LOGGER.info("Execute after script: %s", script)
        execute_simple_command(script, cwd=sdk_root, shell=True, env=local_envs)


def get_local_path_dir(root, relative_path):
    build_folder = Path(root, relative_path)
    if not build_folder.is_dir():
        err_msg = "Folder does not exist or is not accessible: {}".format(build_folder)
        _LOGGER.critical(err_msg)
        raise ValueError(err_msg)
    return build_folder


def build_project(
    temp_dir,
    project,
    absolute_markdown_path,
    sdk_folder,
    global_conf,
    local_conf,
    autorest_bin=None,
):
    absolute_generated_path = Path(temp_dir, project)
    absolute_save_path = Path(temp_dir, "save")
    move_wrapper_files_or_dirs(sdk_folder, absolute_save_path, global_conf, local_conf)
    generate_code(
        absolute_markdown_path,
        global_conf,
        local_conf,
        absolute_generated_path if "output_dir" in local_conf else None,
        autorest_bin,
    )
    move_autorest_files(absolute_generated_path, sdk_folder, global_conf, local_conf)
    move_wrapper_files_or_dirs(absolute_save_path, sdk_folder, global_conf, local_conf)
    delete_extra_files(sdk_folder, global_conf, local_conf)
    write_build_file(sdk_folder, local_conf)
    execute_after_script(sdk_folder, global_conf, local_conf)


def build_libraries(config, skip_callback, restapi_git_folder, sdk_repo, temp_dir, autorest_bin=None):
    """Main method of the the file"""

    global_conf = config["meta"]
    global_conf["autorest_options"] = solve_relative_path(
        global_conf.get("autorest_options", {}), sdk_repo.working_tree_dir
    )
    global_conf["envs"] = solve_relative_path(global_conf.get("envs", {}), sdk_repo.working_tree_dir)
    global_conf["advanced_options"] = solve_relative_path(
        global_conf.get("advanced_options", {}), sdk_repo.working_tree_dir
    )

    for project, local_conf in config.get("projects", {}).items():
        if skip_callback(project, local_conf):
            _LOGGER.info("Skip project %s", project)
            continue
        local_conf["autorest_options"] = solve_relative_path(
            local_conf.get("autorest_options", {}), sdk_repo.working_tree_dir
        )

        markdown_relative_path, optional_relative_paths = get_input_paths(global_conf, local_conf)
        _LOGGER.info(f"Markdown input: {markdown_relative_path}")
        _LOGGER.info(f"Optional inputs: {optional_relative_paths}")

        absolute_markdown_path = None
        if markdown_relative_path:
            absolute_markdown_path = Path(restapi_git_folder, markdown_relative_path).resolve()
        if optional_relative_paths:
            local_conf.setdefault("autorest_options", {})["input-file"] = [
                Path(restapi_git_folder, input_path).resolve() for input_path in optional_relative_paths
            ]

        sdk_folder = sdk_repo.working_tree_dir
        build_project(
            temp_dir,
            project,
            absolute_markdown_path,
            sdk_folder,
            global_conf,
            local_conf,
            autorest_bin,
        )


def generate_sdk_from_git_object(
    git_object,
    branch_name,
    restapi_git_id,
    sdk_git_id,
    base_branch_names,
    *,
    fallback_base_branch_name="main",
    sdk_tag=None,
):
    """Generate SDK from a commit or a PR object.

    git_object is the initial commit/PR from the RestAPI repo. If git_object is a PR, prefer to checkout Github PR "merge_commit_sha"
    restapi_git_id explains where to clone the repo.
    sdk_git_id explains where to push the commit.
    sdk_tag explains what is the tag used in the Readme for the swagger-to-sdk section. If not provided, use sdk_git_id.
    branch_name is the expected branch name in the SDK repo.
    - If this branch exists, use it.
    - If not, use the base branch to create that branch (base branch is where I intend to do my PR)
    - If base_branch_names is not provided, use fallback_base_branch_name as base
    - If this base branch is provided and does not exists, create this base branch first using fallback_base_branch_name (this one is required to exist)

    WARNING:
    This method might push to "branch_name" and "base_branch_name". No push will be made to "fallback_base_branch_name"
    """
    gh_token = os.environ["GH_TOKEN"]
    message_template = DEFAULT_COMMIT_MESSAGE
    autorest_bin = None
    if sdk_tag is None:
        sdk_tag = sdk_git_id

    try:  # Checkout the sha if commit obj
        branched_rest_api_id = restapi_git_id + "@" + git_object.sha
        pr_number = None
    except (
        AttributeError,
        TypeError,
    ):  # This is a PR, don't clone the fork but "base" repo and PR magic commit
        if git_object.merge_commit_sha:
            branched_rest_api_id = git_object.base.repo.full_name + "@" + git_object.merge_commit_sha
        else:
            branched_rest_api_id = git_object.base.repo.full_name
        pr_number = git_object.number

    # Always clone SDK from fallback branch that is required to exist
    branched_sdk_git_id = sdk_git_id + "@" + fallback_base_branch_name

    # I don't know if the destination branch exists, try until it works
    config = None
    branch_list = base_branch_names + [branch_name] + [fallback_base_branch_name]
    for branch in branch_list:
        try:
            config = read_config_from_github(sdk_git_id, branch, gh_token)
        except Exception:
            pass
        else:
            break
    if config is None:
        raise ValueError("Unable to locate configuration in {}".format(branch_list))
    global_conf = config["meta"]

    # If PR is only about a language that this conf can't handle, skip fast
    if not this_conf_will_generate_for_this_pr(git_object, global_conf):
        _LOGGER.info("Skipping this job based on conf not impacted by Git object")
        return

    with tempfile.TemporaryDirectory() as temp_dir:

        clone_dir = Path(temp_dir) / Path(global_conf.get("advanced_options", {}).get("clone_dir", "sdk"))
        _LOGGER.info("Clone dir will be: %s", clone_dir)

        with manage_git_folder(
            gh_token,
            Path(temp_dir) / Path("rest"),
            branched_rest_api_id,
            pr_number=pr_number,
        ) as restapi_git_folder, manage_git_folder(gh_token, clone_dir, branched_sdk_git_id) as sdk_folder:

            readme_files_infered = get_readme_files_from_git_object(git_object, restapi_git_folder)
            _LOGGER.info("Readmes files infered from PR: %s ", readme_files_infered)
            if not readme_files_infered:
                _LOGGER.info("No Readme in PR, quit")
                return

            # SDK part
            sdk_repo = Repo(str(sdk_folder))

            for base_branch in base_branch_names:
                _LOGGER.info("Checkout and create %s", base_branch)
                checkout_and_create_branch(sdk_repo, base_branch)

            _LOGGER.info("Try to checkout destination branch %s", branch_name)
            try:
                sdk_repo.git.checkout(branch_name)
                _LOGGER.info("The branch exists.")
            except GitCommandError:
                _LOGGER.info("Destination branch does not exists")
                # Will be created by do_commit

            configure_user(gh_token, sdk_repo)

            # Look for configuration in Readme
            _LOGGER.info("Extract conf from Readmes for target: %s", sdk_git_id)
            extract_conf_from_readmes(readme_files_infered, restapi_git_folder, sdk_tag, config)
            _LOGGER.info("End of extraction")

            def skip_callback(project, local_conf):
                # We know "project" is based on Path in "readme_files_infered"
                if Path(project) in readme_files_infered:
                    return False
                # Might be a regular project
                markdown_relative_path, optional_relative_paths = get_input_paths(global_conf, local_conf)
                if not (
                    markdown_relative_path in readme_files_infered
                    or any(input_file in readme_files_infered for input_file in optional_relative_paths)
                ):
                    _LOGGER.info(f"In project {project} no files involved in this commit")
                    return True
                return False

            build_libraries(
                config,
                skip_callback,
                restapi_git_folder,
                sdk_repo,
                temp_dir,
                autorest_bin,
            )

            try:
                commit_for_sha = git_object.commit  # Commit
            except AttributeError:
                commit_for_sha = list(git_object.get_commits())[-1].commit  # PR
            message = message_template + "\n\n" + commit_for_sha.message
            commit_sha = do_commit(sdk_repo, message, branch_name, commit_for_sha.sha)
            if commit_sha:
                for base_branch in base_branch_names:
                    sdk_repo.git.push("origin", base_branch, set_upstream=True)
                sdk_repo.git.push("origin", branch_name, set_upstream=True)
                return "https://github.com/{}/commit/{}".format(sdk_git_id, commit_sha)

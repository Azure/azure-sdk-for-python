"""SwaggerToSdk core tools.
"""
from enum import Enum, unique
import json
import logging
import os
import re
import tempfile
from pathlib import Path

import requests

from github import Github, UnknownObjectException

from .autorest_tools import (
    autorest_latest_version_finder,
    autorest_bootstrap_version_finder,
    autorest_swagger_to_sdk_conf,
)
from azure_devtools.ci_tools.github_tools import get_files, GithubLink

_LOGGER = logging.getLogger(__name__)

CONFIG_FILE = "swagger_to_sdk_config_autorest.json"
CONFIG_FILE_DPG = "swagger_to_sdk_config_dpg.json"

DEFAULT_COMMIT_MESSAGE = "Generated from {hexsha}"


def build_file_content():
    autorest_version = autorest_latest_version_finder()
    autorest_bootstrap_version = autorest_bootstrap_version_finder()
    return {
        "autorest": autorest_version,
        "autorest_bootstrap": autorest_bootstrap_version,
    }


def get_repo_tag_meta(meta_conf):
    repotag = meta_conf.get("repotag")
    if repotag:
        return repotag
    # Guess for now, "repotag" should be added everywhere
    if "go" in meta_conf["autorest_options"]:
        return "azure-sdk-for-go"
    if "ruby" in meta_conf["autorest_options"]:
        return "azure-sdk-for-ruby"
    if "java" in meta_conf["autorest_options"]:
        return "azure-sdk-for-java"
    if "nodejs" in meta_conf["autorest_options"]:
        return "azure-sdk-for-node"
    if "typescript" in meta_conf["autorest_options"]:
        return "azure-sdk-for-js"
    raise ValueError("No repotag found or infered")


@unique
class Language(str, Enum):
    GOLANG = "go"
    RUBY = "ruby"
    JAVA = "java"
    NODEJS = "nodejs"
    CSHARP = "csharp"
    PYTHON = "python"
    TYPESCRIPT = "typescript"


def get_language_from_conf(meta_conf):
    """Detect the language based on the default Autorest options.
    Assuming all language use --mylanguage in the config file.
    If I don't find anything, well just say I don't know...

    This is based on autorest language flags.
    :rtype: Language
    """
    autorest_options_lang = set(meta_conf["autorest_options"].keys())
    languages = set()
    for value in Language:
        if value in autorest_options_lang:
            languages.add(value)

    if not languages:
        _LOGGER.warning("No detected language from this conf")
        return None  # I don't what this conf is about?

    language = languages.pop()
    if languages:
        _LOGGER.warning("This SwaggerToSdk conf seems to generate too much language in one call, assume we don't know")
        return None

    return language


def get_context_tag_from_git_object(git_object):
    files_list = [file.filename for file in get_files(git_object)]
    return get_context_tag_from_file_list(files_list)


def get_context_tag_from_file_list(files_list):
    context_tags = set()
    for filename in files_list:
        filepath = Path(filename)
        filename = filepath.as_posix()
        if "/examples/" in filename:
            # Do not compute context for example that are not used in SDK
            continue
        # Match if RP name
        match = re.match(r"specification/(.*)/Microsoft.\w*/(stable|preview)/", filename, re.I)
        if match:
            context_tags.add(match.groups()[0])
            continue
        # Match if stable/preview but not RP like ARM (i.e. Cognitive Services)
        match = re.match(r"specification/(.*)/(stable|preview)/", filename, re.I)
        if match:
            context_tags.add(match.groups()[0])
            continue
        # Match Readme
        # Do it last step, because if some weird Readme for ServiceFabric...
        match = re.match(r"specification/(.*)/readme.\w*.?md", filename, re.I)
        if match:
            context_tags.add(match.groups()[0])
            continue
        # No context-tags
    return context_tags


def this_conf_will_generate_for_this_pr(git_object, config):
    """Try to guess if this PR has a chance to generate something for this conf.

    Right now, just match the language in the conf with the presence
    of ONLY "readme.language.md" files.
    """
    lang = get_language_from_conf(config)
    filenames = [file.filename.lower() for file in get_files(git_object)]
    readme_lang = [name for name in filenames if re.match(r"(.*)readme.\w+.md", name)]

    if len(readme_lang) != len(filenames):
        return True  # This means there is files that are not language specific readme

    return bool([name for name in readme_lang if name.endswith("readme.{}.md".format(lang))])


def get_readme_files_from_git_object(git_object, base_dir=Path(".")):
    files_list = [file.filename for file in get_files(git_object)]
    return get_readme_files_from_file_list(files_list, base_dir)


def get_readme_files_from_file_list(files_list, base_dir=Path(".")):
    """Get readme files from this PR.
    Algo is to look for context, and then search for Readme inside this context.
    """
    readme_files = set()
    context_tags = get_context_tag_from_file_list(files_list)
    for context_tag in context_tags:
        expected_folder = Path(base_dir) / Path("specification/{}".format(context_tag))
        if not expected_folder.is_dir():
            _LOGGER.warning("From context {} I didn't find folder {}".format(context_tag, expected_folder))
            continue
        for expected_readme in [l for l in expected_folder.iterdir() if l.is_file()]:
            # Need to do a case-insensitive test.
            match = re.match(r"readme.\w*.?md", expected_readme.name, re.I)
            if match:
                readme_files.add(expected_readme.relative_to(Path(base_dir)))
    return readme_files


def read_config(sdk_git_folder, config_file):
    """Read the configuration file and return JSON"""
    config_path = os.path.join(sdk_git_folder, config_file)
    with open(config_path, "r") as config_fd:
        return json.loads(config_fd.read())


def read_config_from_github(sdk_id, branch="main", gh_token=None):
    raw_link = str(get_configuration_github_path(sdk_id, branch))
    _LOGGER.debug("Will try to download: %s", raw_link)
    _LOGGER.debug("Token is defined: %s", gh_token is not None)
    headers = {"Authorization": "token {}".format(gh_token)} if gh_token else {}
    response = requests.get(raw_link, headers=headers)
    if response.status_code != 200:
        raise ValueError(
            "Unable to download conf file for SDK {} branch {}: status code {}".format(
                sdk_id, branch, response.status_code
            )
        )
    return json.loads(response.text)


def extract_conf_from_readmes(swagger_files_in_pr, restapi_git_folder, sdk_git_id, config, force_generation=False):
    readme_files_in_pr = {
        readme for readme in swagger_files_in_pr if getattr(readme, "name", readme).lower().endswith("readme.md")
    }
    for readme_file in readme_files_in_pr:
        build_swaggertosdk_conf_from_json_readme(
            readme_file, sdk_git_id, config, base_folder=restapi_git_folder, force_generation=force_generation
        )


def get_readme_path(readme_file, base_folder="."):
    """Get a readable Readme path.

    If start with http, assume online, ignore base_folder and convert to raw link if necessary.
    If base_folder is not None, assume relative to base_folder.
    """
    if not isinstance(readme_file, Path) and readme_file.startswith("http"):
        return GithubLink.from_string(readme_file).as_raw_link()
    else:
        if base_folder is None:
            base_folder = "."
        return str(Path(base_folder) / Path(readme_file))


def build_swaggertosdk_conf_from_json_readme(readme_file, sdk_git_id, config, base_folder=".", force_generation=False):
    """Get the JSON conf of this README, and create SwaggerToSdk conf.

    Readme path can be any readme syntax accepted by autorest.
    readme_file will be project key as-is.

    :param str readme_file: A path that Autorest accepts. Raw GH link or absolute path.
    :param str sdk_dit_id: Repo ID. IF org/login is provided, will be stripped.
    :param dict config: Config where to update the "projects" key.
    :param bool force_generation: If no Swagger to SDK section is found, force once with the Readme as input
    """
    readme_full_path = get_readme_path(readme_file, base_folder)
    with tempfile.TemporaryDirectory() as temp_dir:
        readme_as_conf = autorest_swagger_to_sdk_conf(readme_full_path, temp_dir, config)
    generated_config = {
        "markdown": readme_full_path,
    }
    sdk_git_short_id = sdk_git_id.split("/")[-1].lower()
    _LOGGER.info("Looking for tag {} in readme {}".format(sdk_git_short_id, readme_file))
    for swagger_to_sdk_conf in readme_as_conf:
        if not isinstance(swagger_to_sdk_conf, dict):
            continue
        repo = swagger_to_sdk_conf.get("repo", "")
        repo = repo.split("/")[-1].lower()  # Be sure there is no org/login part
        if repo == sdk_git_short_id:
            _LOGGER.info("This Readme contains a swagger-to-sdk section for repo {}".format(repo))
            generated_config.update(
                {
                    "autorest_options": swagger_to_sdk_conf.get("autorest_options", {}),
                    "after_scripts": swagger_to_sdk_conf.get("after_scripts", []),
                }
            )
            config.setdefault("projects", {})[str(readme_file)] = generated_config
            return generated_config
        else:
            _LOGGER.info("Skip mismatch {} from {}".format(repo, sdk_git_short_id))
    if not force_generation:
        _LOGGER.info(
            "Didn't find tag {} in readme {}. Did you forget to update the SwaggerToSdk section?".format(
                sdk_git_short_id, readme_file
            )
        )
    else:
        _LOGGER.info("Didn't find tag {} in readme {}. Forcing it.".format(sdk_git_short_id, readme_file))
        config.setdefault("projects", {})[str(readme_file)] = generated_config


def get_input_paths(global_conf, local_conf):
    """Returns a 2-tuple:
    - Markdown Path or None
    - Input-file Paths or empty list
    """
    del global_conf  # Unused

    relative_markdown_path = None  # Markdown is optional
    input_files = []  # Input file could be empty
    if "markdown" in local_conf:
        relative_markdown_path = Path(local_conf["markdown"])
    input_files = local_conf.get("autorest_options", {}).get("input-file", [])
    if input_files and not isinstance(input_files, list):
        input_files = [input_files]
    input_files = [Path(input_file) for input_file in input_files]
    if not relative_markdown_path and not input_files:
        raise ValueError("No input file found")
    return (relative_markdown_path, input_files)


def solve_relative_path(autorest_options, sdk_root):
    """Solve relative path in conf.

    If a key is prefixed by "sdkrel:", it's solved against SDK root.
    """
    SDKRELKEY = "sdkrel:"
    solved_autorest_options = {}
    for key, value in autorest_options.items():
        if key.startswith(SDKRELKEY):
            _LOGGER.debug("Found a sdkrel pair: %s/%s", key, value)
            subkey = key[len(SDKRELKEY) :]
            solved_value = Path(sdk_root, value).resolve()
            solved_autorest_options[subkey] = str(solved_value)
        else:
            solved_autorest_options[key] = value
    return solved_autorest_options


def get_configuration_github_path(sdk_id, branch="master"):
    return GithubLink(sdk_id, "raw", branch, CONFIG_FILE)

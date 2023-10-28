import os, tempfile, shutil


import pytest

from typing import List
from ci_tools.functions import replace_dev_reqs

integration_folder = os.path.join(os.path.dirname(__file__), "integration")
sample_dev_reqs_folder = os.path.join(integration_folder, "scenarios", "dev_requirement_samples")
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
core_location = os.path.join(repo_root, "sdk", "core", "azure-core")


def create_temporary_scenario(tmp_directory_create, target_file: str) -> str:
    """
    Creates a temporary directory, copies a target scenario file to it, and returns the path to that copied file.
    """
    tmp_dir = tmp_directory_create([])

    if not os.path.exists(target_file):
        raise Exception("Unable to create a temporary scenario based on a nonexistent requirements file.")
    
    if not os.path.isfile(target_file):
        raise Exception("Unable to create a temporary scenario based on a target that is not actually a file.")

    filename = os.path.basename(target_file)
    move_target = os.path.join(tmp_dir.name, filename)

    shutil.copy(target_file, move_target)

    return (tmp_dir, move_target)
    

def get_requirements_from_file(requirements_file: str) -> List[str]:
    with open(requirements_file, 'r', encoding='utf-8') as f:
        results = f.readlines()

    return [line.strip() for line in results if line.strip()]


def test_replace_dev_reqs_specifiers(tmp_directory_create):
    target_file = os.path.join(sample_dev_reqs_folder, "specifiers_requirements.txt")
    tmp_dir, requirements_file = create_temporary_scenario(tmp_directory_create, target_file)

    try:
        replace_dev_reqs(target_file, core_location)
        actual_requirements = get_requirements_from_file(requirements_file)
    finally:
        tmp_dir.cleanup()


def test_replace_dev_reqs_relative(tmp_directory_create):
    target_file = os.path.join(sample_dev_reqs_folder, 'relative_requirements.txt')
    tmp_dir, requirements_file = create_temporary_scenario(tmp_directory_create, target_file)

    try:
        pass

    finally:
        tmp_dir.cleanup()

def test_replace_dev_reqs_remote(tmp_directory_create):
    target_file = os.path.join(sample_dev_reqs_folder, 'remote_requirements.txt')
    tmp_dir, requirements_file = create_temporary_scenario(tmp_directory_create, target_file)

    try:
        pass

    finally:
        tmp_dir.cleanup()
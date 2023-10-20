import os, tempfile, shutil


import pytest

from ci_tools.functions import replace_dev_reqs

integration_folder = os.path.join(os.path.dirname(__file__), "integration")
sample_dev_reqs_folder = os.path.join(integration_folder, "scenarios", "dev_requirement_samples")

def test_replace_dev_reqs_standard():
    pass

def test_replace_dev_reqs_relative():
    pass

def test_replace_dev_reqs_remote():
    pass
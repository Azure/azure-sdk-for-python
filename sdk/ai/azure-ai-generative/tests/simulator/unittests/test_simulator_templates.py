# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import tempfile
import os
from azure.ai.generative.synthetic.simulator import SimulatorTemplates
from unittest.mock import Mock, patch
from azure.ai.generative.synthetic.simulator import _template_dir as template_dir
from azure.ai.generative.synthetic.simulator.templates._templates import SUMMARIZATION_PATH, SUMMARIZATION

@pytest.mark.unittest
class TestSimulator:
    def test_simulator_templates_get_param(self):
        st = SimulatorTemplates()

        params = st.get_template_parameters(SUMMARIZATION)

        assert set(params.keys()) == set(["name", "chatbot_name", "filename", "file_content"])

    def test_simulator_templates_get(self):
        st = SimulatorTemplates()
        template = st.get_template(SUMMARIZATION)

        with open(os.path.join(template_dir, SUMMARIZATION_PATH), "r") as f:
            read_template = f.read()

        assert str(template) == read_template
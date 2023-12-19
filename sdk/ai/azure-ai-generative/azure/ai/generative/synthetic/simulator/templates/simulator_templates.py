# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.generative.synthetic.simulator.templates._templates import ALL_TEMPLATES, CONTEXT_KEY
from azure.ai.generative.synthetic.simulator import _template_dir as template_dir
from jinja2 import (
    Environment as JinjaEnvironment,
    FileSystemLoader as JinjaFileSystemLoader,
    meta as JinjaMeta,
)
import os

class Template:
    def __init__(self, template_name, text, context_key):
        self.text = text
        self.context_key = context_key
        self.template_name = template_name
        
    def __str__(self):
        return self.text

class SimulatorTemplates:
    def __init__(self):
        self.cached_templates_source = {}
        self.template_env = JinjaEnvironment(
            loader=JinjaFileSystemLoader(searchpath=template_dir)
        )

    def get_templates_list(self):
        return ALL_TEMPLATES.keys()

    def _get_template_context_key(self, template_name):
        return CONTEXT_KEY.get(template_name)

    def get_template(self, template_name):
        if template_name in self.cached_templates_source:
            template, template_path, loader_func = self.cached_templates_source[template_name]
            return Template(template_name, template, self._get_template_context_key(template_name))

        if template_name not in ALL_TEMPLATES.keys():
            raise ValueError(f"{template_name} not in templates library.")

        template_source = self.template_env.loader.get_source(
            self.template_env, ALL_TEMPLATES[template_name]
        )
        self.cached_templates_source[template_name] = template_source

        template, template_path, loader_func = template_source
        return Template(template_name, template, self._get_template_context_key(template_name))

    def get_template_parameters(self, template_name):
        # make sure template is cached
        self.get_template(template_name)

        template_source = self.cached_templates_source[template_name]
        vars = JinjaMeta.find_undeclared_variables(self.template_env.parse(template_source))
        return {k: None for k in vars}

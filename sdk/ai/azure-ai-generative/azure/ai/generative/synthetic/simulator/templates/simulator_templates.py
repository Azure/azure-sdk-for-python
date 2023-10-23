# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.generative.synthetic.simulator.templates._templates import ALL_TEMPLATES
from azure.ai.generative.synthetic.simulator import _template_dir as template_dir
from jinja2 import (
    Environment as JinjaEnvironment,
    FileSystemLoader as JinjaFileSystemLoader,
    meta as JinjaMeta,
)
import os


class SimulatorTemplates:
    def __init__(self):
        self.cached_templates_source = {}
        self.templ_env = JinjaEnvironment(
            loader=JinjaFileSystemLoader(searchpath=template_dir)
        )

    def get_templates_list(self):
        return ALL_TEMPLATES.keys()

    def get_template(self, template_name):
        if template_name in self.cached_templates_source:
            templ, templ_path, loader_func = self.cached_templates_source[template_name]
            return templ

        if template_name not in ALL_TEMPLATES.keys():
            raise ValueError(f"{template_name} not in templates library.")

        template_source = self.templ_env.loader.get_source(
            self.templ_env, ALL_TEMPLATES[template_name]
        )
        self.cached_templates_source[template_name] = template_source

        templ, templ_path, loader_func = template_source
        return templ

    def get_template_parameters(self, template_name):
        # make sure template is cached
        self.get_template(template_name)

        template_source = self.cached_templates_source[template_name]
        vars = JinjaMeta.find_undeclared_variables(self.templ_env.parse(template_source))
        return {k: None for k in vars}

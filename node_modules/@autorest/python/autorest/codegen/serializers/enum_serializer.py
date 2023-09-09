# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from jinja2 import Environment
from ..models import CodeModel


class EnumSerializer:
    def __init__(self, code_model: CodeModel, env: Environment) -> None:
        self.code_model = code_model
        self.env = env

    def serialize(self) -> str:
        # Generate the enum file
        template = self.env.get_template("enum_container.py.jinja2")
        return template.render(code_model=self.code_model)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import re
from typing import Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import ScriptReference as RestScriptReference
from azure.ai.ml._restclient.v2022_10_01_preview.models import ScriptsToExecute as RestScriptsToExecute
from azure.ai.ml._restclient.v2022_10_01_preview.models import SetupScripts as RestSetupScripts
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ScriptReference(RestTranslatableMixin):
    """Script reference.

    :param path: The location of scripts in workspace storage.
    :type path: Optional[str], optional
    :param command: Optional command line arguments passed to the script to run.
    :type command: Optional[str], optional
    :param timeout_minutes: Optional time period passed to timeout command.
    :type timeout_minutes: Optional[int], optional
    """

    def __init__(
        self, *, path: Optional[str] = None, command: Optional[str] = None, timeout_minutes: Optional[int] = None
    ):
        self.path = path
        self.command = command
        self.timeout_minutes = timeout_minutes

    def _to_rest_object(self) -> RestScriptReference:
        return RestScriptReference(
            script_source="workspaceStorage",
            script_data=self.path,
            script_arguments=self.command,
            timeout=f"{self.timeout_minutes}m",
        )

    @classmethod
    def _from_rest_object(cls, obj: RestScriptReference) -> "ScriptReference":
        if obj is None:
            return obj
        timeout_match = re.match(r"(\d+)m", obj.timeout) if obj.timeout else None
        timeout_minutes = timeout_match.group(1) if timeout_match else None
        script_reference = ScriptReference(
            path=obj.script_data if obj.script_data else None,
            command=obj.script_arguments if obj.script_arguments else None,
            timeout_minutes=timeout_minutes,
        )
        return script_reference


class SetupScripts(RestTranslatableMixin):
    """Customized setup scripts.

    :param startup_script: Script that's run every time the machine starts.
    :type startup_script: Optional[ScriptReference], optional
    :param creation_script: Script that's run only once during provision of the compute.
    :type creation_script: Optional[ScriptReference], optional
    """

    def __init__(
        self, *, startup_script: Optional[ScriptReference] = None, creation_script: Optional[ScriptReference] = None
    ):
        self.startup_script = startup_script
        self.creation_script = creation_script

    def _to_rest_object(self) -> RestScriptsToExecute:
        scripts_to_execute = RestScriptsToExecute(
            startup_script=self.startup_script._to_rest_object() if self.startup_script else None,
            creation_script=self.creation_script._to_rest_object() if self.creation_script else None,
        )
        return RestSetupScripts(scripts=scripts_to_execute)

    @classmethod
    def _from_rest_object(cls, obj: RestSetupScripts) -> "SetupScripts":
        if obj is None or obj.scripts is None:
            return None
        scripts = obj.scripts
        setup_scripts = SetupScripts(
            startup_script=ScriptReference._from_rest_object(
                scripts.startup_script if scripts.startup_script else None
            ),
            creation_script=ScriptReference._from_rest_object(
                scripts.creation_script if scripts.creation_script else None
            ),
        )
        return setup_scripts

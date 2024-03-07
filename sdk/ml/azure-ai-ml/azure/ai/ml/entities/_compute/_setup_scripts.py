# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import re
from typing import Optional, cast

from azure.ai.ml._restclient.v2022_10_01_preview.models import ScriptReference as RestScriptReference
from azure.ai.ml._restclient.v2022_10_01_preview.models import ScriptsToExecute as RestScriptsToExecute
from azure.ai.ml._restclient.v2022_10_01_preview.models import SetupScripts as RestSetupScripts
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ScriptReference(RestTranslatableMixin):
    """Script reference.

    :keyword path: The location of scripts in workspace storage.
    :paramtype path: Optional[str]
    :keyword command: Command line arguments passed to the script to run.
    :paramtype command: Optional[str]
    :keyword timeout_minutes: Timeout, in minutes, for the script to run.
    :paramtype timeout_minutes: Optional[int]
    """

    def __init__(
        self, *, path: Optional[str] = None, command: Optional[str] = None, timeout_minutes: Optional[int] = None
    ) -> None:
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
    def _from_rest_object(cls, obj: RestScriptReference) -> Optional["ScriptReference"]:
        if obj is None:
            return obj
        timeout_match = re.match(r"(\d+)m", obj.timeout) if obj.timeout else None
        timeout_minutes = timeout_match.group(1) if timeout_match else None
        script_reference = ScriptReference(
            path=obj.script_data if obj.script_data else None,
            command=obj.script_arguments if obj.script_arguments else None,
            timeout_minutes=cast(Optional[int], timeout_minutes),
        )
        return script_reference


class SetupScripts(RestTranslatableMixin):
    """Customized setup scripts.

    :keyword startup_script: The script to be run every time the compute is started.
    :paramtype startup_script: Optional[~azure.ai.ml.entities.ScriptReference]
    :keyword creation_script: The script to be run only when the compute is created.
    :paramtype creation_script: Optional[~azure.ai.ml.entities.ScriptReference]
    """

    def __init__(
        self, *, startup_script: Optional[ScriptReference] = None, creation_script: Optional[ScriptReference] = None
    ) -> None:
        self.startup_script = startup_script
        self.creation_script = creation_script

    def _to_rest_object(self) -> RestScriptsToExecute:
        scripts_to_execute = RestScriptsToExecute(
            startup_script=self.startup_script._to_rest_object() if self.startup_script else None,
            creation_script=self.creation_script._to_rest_object() if self.creation_script else None,
        )
        return RestSetupScripts(scripts=scripts_to_execute)

    @classmethod
    def _from_rest_object(cls, obj: RestSetupScripts) -> Optional["SetupScripts"]:
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

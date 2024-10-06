# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Optional, Literal, overload
import sys
import os
import functools

import click
from flask import g, current_app, Flask

from ._version import VERSION

from azure.cloudmachine._client import (
    CloudMachineClient,
    CloudMachineStorage,
    CloudMachineTableData,
    load_dev_environment,
)
from azure.cloudmachine.resources import (
    CloudMachineDeployment,
    init_project,
    run_project,
    shutdown_project
)

__version__ = VERSION


# class User:
#     storage: CloudMachineStorage

#     @property
#     def storage(self) -> CloudMachineStorage:
#         if not current_app:
#             raise RuntimeError("CloudMachine only availble within an app context.")
#         return CloudMachineStorage()


class CloudMachineSession:

    def __init__(self, **kwargs):
        self._client = CloudMachineClient(**kwargs)

    def close(self):
        self._client.close()

    @property
    def storage(self) -> CloudMachineStorage:
        if not current_app:
            raise RuntimeError("CloudMachineSession only availble within an app context.")
        return self._client.storage

    @property
    def data(self) -> CloudMachineTableData:
        if not current_app:
            raise RuntimeError("CloudMachineSession only availble within an app context.")
        return self._client.data

    # @property
    # def user(self) -> User:
    #     if not current_app:
    #         raise RuntimeError("CloudMachine only availble within an app context.")
    #     if not self.authenticated:
    #         raise RuntimeError("CloudMachine is not current user-authenticated.")
    #     return User()


class CloudMachine:
    deployment: Optional[CloudMachineDeployment]
    label: Optional[str]

    @overload
    def __init__(
            self,
            app: Optional[Flask] = None,
            *,
            name: Optional[str] = None,
            label: Optional[str] = None,
            location: Optional[str] = None,
            host: Literal["local", "appservice", "containerapp"] = "local"
    ):
        ...
    @overload
    def __init__(
            self,
            app: Optional[Flask] = None,
            *,
            deployment: Optional[CloudMachineDeployment],
            label: Optional[str] = None,
    ):
        ...
    def __init__(self, app = None, **kwargs):
        self._session: Optional[CloudMachineSession] = None
        self._location = kwargs.get('location')
        self._host = kwargs.get('host')
        self._name = kwargs.get('name')
        self.deployment = kwargs.get('deployment')
        self.label = kwargs.get('label') 
        if app is not None:
            self.init_app(app)

    @property
    def session(self) -> CloudMachineSession:
        if not current_app:
            raise RuntimeError("CloudMachineSession only availble within an app context.")
        if not self._session:
            self._session = CloudMachineSession()
        return self._session

    def init_app(self, app: Flask) -> None:
        if not self._name and 'CLOUDMACHINE_NAME' not in app.config:
            raise ValueError("CloudMachine must have a name, either passed at constructor, or via CLOUDMACHINE_NAME config.")
        self.label = self.label or app.config.get('CLOUDMACHINE_LABEL')
        if not self.deployment:
            self.deployment = CloudMachineDeployment(
                name=self._name or app.config.get('CLOUDMACHINE_NAME'),
                location=self._location or app.config.get('CLOUDMACHINE_LOCATION'),
                host=self._host or app.config.get('CLOUDMACHINE_HOST') or 'local'
            )

        if 'cm' in sys.argv:
            cmd_infra = functools.partial(cm_infra, self)
            if self.deployment.host == 'local':
                cmd_run = functools.partial(cm_run_local, self)
            else:
                cmd_run = functools.partial(cm_run_remote, self)
            cmd_down = functools.partial(cm_down, self)
            app.cli.add_command(
                click.Group(
                    'cm',
                    commands=[
                        click.Command('infra', callback=cmd_infra,),
                        click.Command('run', callback=cmd_run),
                        click.Command('down', callback=cmd_down)
                    ]
                )
            )
        else:
            if self.deployment.host == 'local':
                # TODO: rmeove dotenv to use app.config.from_file
                app.config.update(load_dev_environment(self.deployment.name))
            else:
                app.config.from_prefixed_env(prefix='AZURE_CLOUDMACHINE_')
        app.before_request(self._create_session)
        app.teardown_appcontext(self._close_session)
        
    def _create_session(self, *args) -> None:
        if not hasattr(g, 'cloudmachine'):
            g.cloudmachine = CloudMachineSession()

    def _close_session(self, *args) -> None:
        if hasattr(g, 'cloudmachine'):
            g.cloudmachine.close()


def cm_infra(cm: CloudMachine) -> None:
    init_project(
        os.getcwd(),
        cm.deployment,
        cm.label)
    cm.deployment.write(os.getcwd())

def cm_run_local(cm: CloudMachine) -> None:
    cm_infra(cm)
    args = sys.argv[sys.argv.index('flask'): sys.argv.index('cm')]
    run_project(cm.deployment, cm.label, args)

def cm_down(cm: CloudMachine) -> None:
    shutdown_project(cm.deployment, cm.label)

def cm_run_remote(cm: CloudMachine) -> None:
    raise NotImplementedError()

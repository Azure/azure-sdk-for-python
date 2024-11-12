# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Optional, Literal, overload, Union
import sys
import os
import functools

import click
from flask import g, current_app, Flask

from ._version import VERSION

from azure.cloudmachine._client import (
    CloudMachineClient,
    load_dev_environment,
)
from azure.cloudmachine._resources._client_settings import ClientSettings
from azure.cloudmachine.provisioning import (
    CloudMachineDeployment,
    init_project,
    provision_project,
    shutdown_project,
    deploy_project
)

__version__ = VERSION


class CloudMachine(CloudMachineClient):
    label: Optional[str]
    deployment: CloudMachineDeployment

    @overload
    def __init__(
            self,
            app: Optional[Flask] = None,
            *,
            name: Optional[str] = None,
            label: Optional[str] = None,
            location: Optional[str] = None,
            host: Literal["local", "appservice", "containerapp"] = "local",
            openai: Optional[Union[ClientSettings, str]] = None,
            data: Optional[Union[ClientSettings, str]] = None,
            messaging: Optional[Union[ClientSettings, str]] = None,
            storage: Optional[Union[ClientSettings, str]] = None,
            search: Optional[Union[ClientSettings, str]] = None,
            documentai: Optional[Union[ClientSettings, str]] = None,
    ):
        ...
    @overload
    def __init__(
            self,
            app: Optional[Flask] = None,
            *,
            deployment: CloudMachineDeployment,
            label: Optional[str] = None,
            openai: Optional[Union[ClientSettings, str]] = None,
            data: Optional[Union[ClientSettings, str]] = None,
            messaging: Optional[Union[ClientSettings, str]] = None,
            storage: Optional[Union[ClientSettings, str]] = None,
            search: Optional[Union[ClientSettings, str]] = None,
            documentai: Optional[Union[ClientSettings, str]] = None,
    ):
        ...
    def __init__(
            self,
            app = None,
            *,
            name: Optional[str] = None,
            label: Optional[str] = None,
            location: Optional[str] = None,
            host: Literal["local", "appservice", "containerapp"] = "local",
            deployment: Optional[CloudMachineDeployment] = None,
            openai: Optional[Union[ClientSettings, str]] = None,
            data: Optional[Union[ClientSettings, str]] = None,
            messaging: Optional[Union[ClientSettings, str]] = None,
            storage: Optional[Union[ClientSettings, str]] = None,
            search: Optional[Union[ClientSettings, str]] = None,
            documentai: Optional[Union[ClientSettings, str]] = None,
    ):
        self._location = location
        self._host = host
        self._name = name
        super().__init__(
            deployment=deployment,
            openai=openai,
            data=data,
            messaging=messaging,
            storage=storage,
            search=search,
            documentai=documentai
        )
        if self.deployment:
            self._name = self.deployment.name
        self.label = label
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if not self._name and 'AZURE_CLOUDMACHINE_NAME' not in app.config:
            raise ValueError("CloudMachine must have a name, either passed at constructor, or via CLOUDMACHINE_NAME config.")
        self.label = self.label or app.config.get('AZURE_CLOUDMACHINE_LABEL')
        if not self.deployment:
            self.deployment = CloudMachineDeployment(
                name=self._name or app.config.get('AZURE_CLOUDMACHINE_NAME'),
                location=self._location or app.config.get('AZURE_CLOUDMACHINE_LOCATION'),
                host=self._host or app.config.get('AZURE_CLOUDMACHINE_HOST') or 'local'
            )
        #for client_settings in self._settings.values():
        #    if client_settings is not None:
        #        client_settings.add_config_store(app.config)

        if 'cm' in sys.argv:
            cmd_infra = functools.partial(cm_infra, self)
            if self.deployment.host == 'local':
                cmd_provision = functools.partial(cm_provision_local, self)
            else:
                cmd_provision = functools.partial(cm_provision_remote, self)
            cmd_down = functools.partial(cm_down, self)
            app.cli.add_command(
                click.Group(
                    'cm',
                    commands=[
                        click.Command('infra', callback=cmd_infra,),
                        click.Command('provision', callback=cmd_provision),
                        click.Command('down', callback=cmd_down)
                    ]
                )
            )
        else:
            if self.deployment.host == 'local':
                os.environ.update(self.deployment.app_settings)
                app.config.update(load_dev_environment(self.deployment.name))
            else:
                app.config.from_prefixed_env(prefix='AZURE_')
        # app.before_request(self._create_session)
        # app.teardown_appcontext(self._close_session)
        
    # def _create_session(self, *args) -> None:
    #     if not hasattr(g, 'cloudmachine'):
    #         g.cloudmachine = CloudMachineSession()

    # def _close_session(self, *args) -> None:
    #     if hasattr(g, 'cloudmachine'):
    #         g.cloudmachine.close()


def cm_infra(cm: CloudMachine) -> None:
    init_project(
        os.getcwd(),
        cm.deployment,
        cm.label,
        metadata={'cloudmachine-flask': VERSION}
    )
    cm.deployment.write(os.getcwd())

def cm_provision_local(cm: CloudMachine) -> None:
    cm_infra(cm)
    provision_project(cm.deployment, cm.label)

def cm_down(cm: CloudMachine) -> None:
    shutdown_project(cm.deployment, cm.label)

def cm_provision_remote(cm: CloudMachine) -> None:
    cm_infra(cm)
    deploy_project(cm.deployment, cm.label)

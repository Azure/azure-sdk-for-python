# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines

from ._generated.models import EventRoute as GeneratedEventRoute

class DigitalTwinsEventRoute(GeneratedEventRoute):
    """A route which directs notification and telemetry events to an endpoint.
        Endpoints are a destination outside of Azure Digital Twins such as an EventHub.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :keyword str id: The id of the event route.
    :keyword str endpoint_name: The name of the endpoint this event route is bound to.
    :keyword str filter: An expression which describes the events which are routed to the endpoint.
    """

    def __init__(self, **kwargs):
        self.id = None
        self.endpoint_name = kwargs['endpoint_name']
        self.filter = kwargs['filter']
    
    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            id=generated.id,
            endpoint_name=generated.endpoint_name,
            filter=generated.filter
        )

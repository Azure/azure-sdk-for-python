# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

""" Custom Async Polling Methods for Azure Batch Operations."""

import asyncio
import time

from typing import Any, Callable, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline import PipelineResponse
from azure.core.polling import AsyncPollingMethod

from ... import models as _models


class DeleteJobPollingMethodAsync(AsyncPollingMethod):
    """Polling method for job delete operation.

    This class is used to poll the status of a job deletion operation.
    It checks the status of the job until it is deleted or an error occurs.
    """

    def __init__(self, job_id: str, polling_interval: int = 5):
        # remove client to keep in initialize
        self._job_id = job_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = await self._client.get_job(self._job_id)

            # check job state is DELETING state (if not in deleting state then it's succeeded)
            if job.state != _models.BatchJobState.DELETING:
                self._status = "Succeeded"
                self._finished = True
            
        # testing an invalid job_id will throw a JobNotFound error before actually building the poller
        # probably don't need this?

        except ResourceNotFoundError: 
            # Job no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class DisableJobPollingMethodAsync(AsyncPollingMethod):
    """Polling method for job disable operation.

    This class is used to poll the status of a job disable operation.
    It checks the status of the job until it is disabled or an error occurs.
    """

    def __init__(self, job_id: str, polling_interval: int = 5):
        self._job_id = job_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = await self._client.get_job(self._job_id)

            # check job state is not in DISABLING for success
            if job.state != _models.BatchJobState.DISABLING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Job no longer exists, unexpected for disable operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class EnableJobPollingMethodAsync(AsyncPollingMethod):
    """Polling method for job enable operation.
    
    This class is used to poll the status of a job enable operation.
    It checks the status of the job until it is enabled or an error occurs.
    """

    def __init__(self, job_id: str, polling_interval: int = 5):
        self._job_id = job_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = await self._client.get_job(self._job_id)

            # if job is not enabling then done
            if job.state != _models.BatchJobState.ENABLING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Job no longer exists, unexpected for enable operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class DeleteJobSchedulePollingMethodAsync(AsyncPollingMethod):
    """Polling method for job schedule delete operation.
    
    This class is used to poll the status of a job schedule deletion operation.
    It checks the status of the job schedule until it is deleted or an error occurs.
    """

    def __init__(self, job_schedule_id: str, polling_interval: int = 5):
        # remove client to keep in initialize
        self._job_schedule_id = job_schedule_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job_schedule = await self._client.get_job_schedule(self._job_schedule_id)

            # check job schedule state is DELETING state (if not in deleting state then it's succeeded)
            if job_schedule.state != _models.BatchJobScheduleState.DELETING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Job schedule no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class DeletePoolPollingMethodAsync(AsyncPollingMethod):
    """Polling method for pool delete operation.
    This class is used to poll the status of a pool deletion operation.
    It checks the status of the pool until it is deleted or an error occurs.
    """
    def __init__(self, pool_id: str, polling_interval: int = 5):
        # remove client to keep in initialize
        self._pool_id = pool_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False
        
    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = await self._client.get_pool(self._pool_id)

            # check pool state is DELETING state (if not in deleting state then it's succeeded)
            if pool.state != _models.BatchPoolState.DELETING:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Pool no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class DeleteCertificatePollingMethodAsync(AsyncPollingMethod):
    """Polling method for certificate delete operation.
    
    This class is used to poll the status of a certificate deletion operation.
    It checks the status of the certificate until it is deleted or an error occurs.
    """

    def __init__(self, thumbprint_algorithm: str, thumbprint: str, polling_interval: int = 5):
        self._thumbprint_algorithm = thumbprint_algorithm
        self._thumbprint = thumbprint
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            certificate = await self._client.get_certificate(self._thumbprint_algorithm, self._thumbprint)

            # check certificate state is DELETING state (if not in deleting state then it's succeeded)
            if certificate.state != _models.BatchCertificateState.DELETING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Certificate no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class DeallocateNodePollingMethodAsync(AsyncPollingMethod):
    """Polling method for node deallocate operation.
    
    This class is used to poll the status of a node deallocation operation.
    It checks the status of the node until it is deallocated or an error occurs.
    """

    def __init__(self, pool_id: str, node_id: str, polling_interval: int = 5):
        self._pool_id = pool_id
        self._node_id = node_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = await self._client.get_node(self._pool_id, self._node_id)

            # If node not in DEALLOCATING state then completed
            # don't check DEALLOCATED (too quick of a state to check?)
            if node.state != _models.BatchNodeState.DEALLOCATING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Node no longer exists, might have been removed from pool
            self._status = "Succeeded"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class RebootNodePollingMethodAsync(AsyncPollingMethod):
    """Polling method for node reboot operation.
    
    This class is used to poll the status of a node reboot operation.
    It checks the status of the node until it is rebooted or an error occurs.
    """

    def __init__(self, pool_id: str, node_id: str, polling_interval: int = 5):
        self._pool_id = pool_id
        self._node_id = node_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = await self._client.get_node(self._pool_id, self._node_id)

            # Node reboot is complete when it's no longer in REBOOTING state
            if node.state != _models.BatchNodeState.REBOOTING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Node no longer exists, unexpected for reboot operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class ReimageNodePollingMethodAsync(AsyncPollingMethod):
    """Polling method for node reimage operation.
    
    This class is used to poll the status of a node reimage operation.
    It checks the status of the node until it is reimaged or an error occurs.
    """

    def __init__(self, pool_id: str, node_id: str, polling_interval: int = 5):
        self._pool_id = pool_id
        self._node_id = node_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = await self._client.get_node(self._pool_id, self._node_id)

            # Node reimage is complete when it's no longer in REIMAGING state
            if node.state != _models.BatchNodeState.REIMAGING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Node no longer exists, unexpected for reimage operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class RemoveNodePollingMethodAsync(AsyncPollingMethod):
    """Polling method for node remove operation.
    
    This class is used to poll the status of a node removal operation.
    It checks the status of the node until it is removed or an error occurs.
    """

    def __init__(self, pool_id: str, polling_interval: int = 5):
        self._pool_id = pool_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = await self._client.get_pool(self._pool_id)

            # Node removal is complete when the pool allocation state is STEADY
            # This means the pool is no longer resizing/removing nodes
            if pool.allocation_state == _models.AllocationState.STEADY:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Pool no longer exists, unexpected for remove node operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class ResizePoolPollingMethodAsync(AsyncPollingMethod):
    """Polling method for pool resize operation.
    
    This class is used to poll the status of a pool resize operation.
    It checks the status of the pool until it is resized or an error occurs.
    """

    def __init__(self, pool_id: str, polling_interval: int = 5):
        self._pool_id = pool_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = await self._client.get_pool(self._pool_id)

            # Pool resize is complete when the pool allocation state is STEADY
            # This means the pool is no longer resizing (adding/removing nodes)
            if pool.allocation_state == _models.AllocationState.STEADY:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Pool no longer exists, unexpected for resize operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class StartNodePollingMethodAsync(AsyncPollingMethod):
    """Polling method for node start operation.
    
    This class is used to poll the status of a node start operation.
    It checks the status of the node until it is started or an error occurs.
    """

    def __init__(self, pool_id: str, node_id: str, polling_interval: int = 5):
        self._pool_id = pool_id
        self._node_id = node_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = await self._client.get_node(self._pool_id, self._node_id)

            # Node start is complete when it's no longer in STARTING state
            if node.state != _models.BatchNodeState.STARTING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Node no longer exists, unexpected for start operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class StopPoolResizePollingMethodAsync(AsyncPollingMethod):
    """Polling method for pool stop resize operation.
    
    This class is used to poll the status of a pool stop resize operation.
    It checks the status of the pool until it is stopped or an error occurs.
    """

    def __init__(self, pool_id: str, polling_interval: int = 5):
        self._pool_id = pool_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = await self._client.get_pool(self._pool_id)

            # Pool stop resize is complete when the pool allocation state is STEADY
            # This means the pool has stopped resizing and is stable
            if pool.allocation_state == _models.AllocationState.STEADY:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Pool no longer exists, unexpected for stop resize operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class TerminateJobPollingMethodAsync(AsyncPollingMethod):
    """Polling method for job termination operation.
    
    This class is used to poll the status of a job termination operation.
    It checks the status of the job until it is terminated or an error occurs.
    """

    def __init__(self, job_id: str, polling_interval: int = 5):
        self._job_id = job_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = await self._client.get_job(self._job_id)

            # Job termination is complete when it's no longer in TERMINATING state
            if job.state != _models.BatchJobState.TERMINATING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Job no longer exists, unexpected for terminate operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False


class TerminateJobSchedulePollingMethodAsync(AsyncPollingMethod):
    """Polling method for job schedule termination operation.
    
    This class is used to poll the status of a job schedule termination operation.
    It checks the status of the job schedule until it is terminated or an error occurs.
    """

    def __init__(self, job_schedule_id: str, polling_interval: int = 5):
        self._job_schedule_id = job_schedule_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    async def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            await self.update_status()
            if not self.finished():
                # add a delay if not done
                await asyncio.sleep(self._polling_interval)

    async def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job_schedule = await self._client.get_job_schedule(self._job_schedule_id)

            # Job schedule termination is complete when it's no longer in TERMINATING state
            if job_schedule.state != _models.BatchJobScheduleState.TERMINATING:
                self._status = "Succeeded"
                self._finished = True
            
        except ResourceNotFoundError: 
            # Job schedule no longer exists, unexpected for terminate operation
            self._status = "Failed"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False
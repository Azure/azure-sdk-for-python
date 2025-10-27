# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

""" Custom Sync Polling Methods for Azure Batch Operations."""

import time
from typing import Any, Callable, Optional

from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.core.pipeline import PipelineResponse
from azure.core.polling import PollingMethod

from .. import models as _models


class DeleteJobPollingMethod(PollingMethod):
    """Polling method for job delete operation.

    This class is used to poll the status of a job deletion operation.
    It checks the status of the job until it is deleted or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        job_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._job_id = job_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = self._client.get_job(self._job_id)

            if job.state == _models.BatchJobState.DELETING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Job no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Some other error occurred, operation failed
            self._status = "Failed"
            self._finished = True


class DisableJobPollingMethod(PollingMethod):
    """Polling method for job disable operation.

    This class is used to poll the status of a job disable operation.
    It checks the status of the job until it is disabled or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        job_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False
        self._job_id = job_id
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = self._client.get_job(self._job_id)

            if job.state == _models.BatchJobState.DISABLING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # If job doesn't exist it could've been deleted while disabling
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class EnableJobPollingMethod(PollingMethod):
    """Polling method for job enable operation.

    This class is used to poll the status of a job enable operation.
    It checks the status of the job until it is enabled or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        job_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._job_id = job_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = self._client.get_job(self._job_id)

            if job.state == _models.BatchJobState.ENABLING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # If job doesn't exist it could've been deleted while enabling
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class DeleteJobSchedulePollingMethod(PollingMethod):
    """Polling method for job schedule delete operation.

    This class is used to poll the status of a job schedule deletion operation.
    It checks the status of the job schedule until it is deleted or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        job_schedule_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._job_schedule_id = job_schedule_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job_schedule = self._client.get_job_schedule(self._job_schedule_id)

            if job_schedule.state == _models.BatchJobScheduleState.DELETING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Job schedule no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class DeletePoolPollingMethod(PollingMethod):
    """Polling method for pool delete operation.
    This class is used to poll the status of a pool deletion operation.
    It checks the status of the pool until it is deleted or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = self._client.get_pool(self._pool_id)

            if pool.state == _models.BatchPoolState.DELETING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Pool no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class DeleteCertificatePollingMethod(PollingMethod):
    """Polling method for certificate delete operation.

    This class is used to poll the status of a certificate deletion operation.
    It checks the status of the certificate until it is deleted or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        thumbprint_algorithm: str,
        thumbprint: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._thumbprint_algorithm = thumbprint_algorithm
        self._thumbprint = thumbprint
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            certificate = self._client.get_certificate(self._thumbprint_algorithm, self._thumbprint)

            # check certificate state is DELETING state (if not in deleting state then it's succeeded)
            if certificate.state == _models.BatchCertificateState.DELETING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Certificate no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class DeallocateNodePollingMethod(PollingMethod):
    """Polling method for node deallocate operation.

    This class is used to poll the status of a node deallocation operation.
    It checks the status of the node until it is deallocated or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        node_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._node_id = node_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = self._client.get_node(self._pool_id, self._node_id)

            # If node not in DEALLOCATING state then completed
            # DEALLOCATED is too quick of a state to check for success
            if node.state == _models.BatchNodeState.DEALLOCATING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Node no longer exists, might have been removed from pool
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class RebootNodePollingMethod(PollingMethod):
    """Polling method for node reboot operation.

    This class is used to poll the status of a node reboot operation.
    It checks the status of the node until it is rebooted or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        node_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._node_id = node_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = self._client.get_node(self._pool_id, self._node_id)

            if node.state == _models.BatchNodeState.REBOOTING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Node could be deleted while rebooting
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class ReimageNodePollingMethod(PollingMethod):
    """Polling method for node reimage operation.

    This class is used to poll the status of a node reimage operation.
    It checks the status of the node until it is reimaged or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        node_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._node_id = node_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = self._client.get_node(self._pool_id, self._node_id)

            if node.state == _models.BatchNodeState.REIMAGING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Node could be deleted while reimaging
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class RemoveNodePollingMethod(PollingMethod):
    """Polling method for node remove operation.

    This class is used to poll the status of a node removal operation.
    It checks the status of the node until it is removed or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = self._client.get_pool(self._pool_id)

            # Node removal is complete when the pool allocation state is STEADY
            # This means the pool is no longer resizing/removing nodes
            if pool.allocation_state == _models.AllocationState.STEADY:
                self._status = "Succeeded"
                self._finished = True
            else:
                self._status = "InProgress"
                self._finished = False

        except ResourceNotFoundError:
            # Pool could be deleted while removing nodes
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class ResizePoolPollingMethod(PollingMethod):
    """Polling method for pool resize operation.

    This class is used to poll the status of a pool resize operation.
    It checks the status of the pool until it is resized or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = self._client.get_pool(self._pool_id)

            # Pool resize is complete when the pool allocation state is STEADY
            # This means the pool is no longer resizing (adding/removing nodes)
            if pool.allocation_state == _models.AllocationState.STEADY:
                self._status = "Succeeded"
                self._finished = True
            else:
                self._status = "InProgress"
                self._finished = False

        except ResourceNotFoundError:
            # Pool could be deleted while resizing
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class StartNodePollingMethod(PollingMethod):
    """Polling method for node start operation.

    This class is used to poll the status of a node start operation.
    It checks the status of the node until it is started or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        node_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._node_id = node_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            node = self._client.get_node(self._pool_id, self._node_id)

            if node.state == _models.BatchNodeState.STARTING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Node could be deleted during starting
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class StopPoolResizePollingMethod(PollingMethod):
    """Polling method for pool stop resize operation.

    This class is used to poll the status of a pool stop resize operation.
    It checks the status of the pool until it is stopped or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        pool_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._pool_id = pool_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            pool = self._client.get_pool(self._pool_id)

            # Pool stop resize is complete when the pool allocation state is STEADY
            # This means the pool has stopped resizing and is stable
            if pool.allocation_state == _models.AllocationState.STEADY:
                self._status = "Succeeded"
                self._finished = True
            else:
                self._status = "InProgress"
                self._finished = False

        except ResourceNotFoundError:
            # Pool could be deleted during stop resize operation
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class TerminateJobPollingMethod(PollingMethod):
    """Polling method for job termination operation.

    This class is used to poll the status of a job termination operation.
    It checks the status of the job until it is terminated or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        job_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._job_id = job_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = self._client.get_job(self._job_id)

            if job.state == _models.BatchJobState.TERMINATING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Job could be deleted while terminating
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True


class TerminateJobSchedulePollingMethod(PollingMethod):
    """Polling method for job schedule termination operation.

    This class is used to poll the status of a job schedule termination operation.
    It checks the status of the job schedule until it is terminated or an error occurs.
    """

    def __init__(
        self,
        client: Any,
        initial_response: PipelineResponse,
        deserialization_callback: Optional[Callable],
        job_schedule_id: str,
        polling_interval: int = 5,
    ):
        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._job_schedule_id = job_schedule_id
        self._status = "InProgress"
        self._finished = False
        self._polling_interval = polling_interval

    def initialize(
        self, client: Any, initial_response: PipelineResponse, deserialization_callback: Optional[Callable]
    ) -> None:
        pass

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> Optional[Any]:
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self) -> None:
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job_schedule = self._client.get_job_schedule(self._job_schedule_id)

            # Job schedule termination is complete when it's no longer in TERMINATING state
            if job_schedule.state == _models.BatchJobScheduleState.TERMINATING:
                self._status = "InProgress"
                self._finished = False
            else:
                self._status = "Succeeded"
                self._finished = True

        except ResourceNotFoundError:
            # Job schedule could be deleted while terminating
            self._status = "Succeeded"
            self._finished = True
        except AzureError:
            # Another error occurred so LRO failed
            self._status = "Failed"
            self._finished = True

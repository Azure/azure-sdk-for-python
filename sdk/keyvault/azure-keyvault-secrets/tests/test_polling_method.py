# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.keyvault.secrets._shared._polling import DeleteRecoverPollingMethod

from _shared.helpers import mock, mock_response

SLEEP = DeleteRecoverPollingMethod.__module__ + ".time.sleep"

raise_exception = lambda message: mock.Mock(side_effect=Exception(message))


def test_initialized_finished():
    """When the polling method is initialized as finished, it shouldn't invoke the command or sleep"""

    command = raise_exception("polling method shouldn't invoke the command")
    polling_method = DeleteRecoverPollingMethod(command, final_resource=None, finished=True)

    assert polling_method.finished()

    with mock.patch(SLEEP, raise_exception("the polling method shouldn't sleep")):
        polling_method.run()


def test_continues_polling_when_resource_not_found():
    class _command:
        calls = 0
        operation_complete = False

    def command():
        """Simulate service responding 404 a few times before 2xx"""

        assert not _command.operation_complete, "polling method shouldn't invoke the command after completion"

        if _command.calls < 3:
            _command.calls += 1
            raise ResourceNotFoundError()

        _command.operation_complete = True

    polling_method = DeleteRecoverPollingMethod(command, final_resource=None, finished=False)

    with mock.patch(SLEEP) as sleep:
        polling_method.run()

    assert sleep.call_count == _command.calls


def test_run_idempotence():
    """After the polling method completes, calling 'run' again shouldn't change state or invoke the command"""

    max_calls = 3

    class _command:
        calls = 0
        operation_complete = False

    def command():
        """Simulate service responding 404 a few times before 2xx"""

        assert not _command.operation_complete, "polling method shouldn't invoke the command after completion"

        if _command.calls < max_calls:
            _command.calls += 1
            raise ResourceNotFoundError()

        _command.operation_complete = True

    resource = object()
    polling_method = DeleteRecoverPollingMethod(command, final_resource=resource, finished=False)
    assert not polling_method.finished()

    with mock.patch(SLEEP) as sleep:
        # when run is first called, the polling method should invoke the command until it indicates completion
        polling_method.run()
    assert _command.calls == max_calls
    assert sleep.call_count == _command.calls

    # invoking run again should not change the resource or finished status, invoke the command, or sleep
    with mock.patch(SLEEP, raise_exception("polling method shouldn't sleep when 'run' is called after completion")):
        for _ in range(4):
            assert polling_method.resource() is resource
            assert polling_method.finished()
            polling_method.run()


def test_final_resource():
    """The polling method should always expose the final resource"""

    resource = object()

    assert DeleteRecoverPollingMethod(command=None, final_resource=resource, finished=True).resource() is resource

    command = mock.Mock()
    polling_method = DeleteRecoverPollingMethod(command, final_resource=resource, finished=False)

    assert polling_method.resource() is resource
    polling_method.run()
    assert polling_method.resource() is resource


def test_terminal_first_response():
    """The polling method shouldn't sleep when Key Vault's first response indicates the operation is complete"""

    command = mock.Mock()
    polling_method = DeleteRecoverPollingMethod(command, final_resource=None, finished=False)

    with mock.patch(SLEEP, raise_exception("polling method shouldn't sleep after the operation completes")):
        polling_method.run()

    assert command.call_count == 1
    assert polling_method.finished()


def test_propagates_unexpected_error():
    """The polling method should raise when Key Vault responds with an unexpected error"""

    response = mock_response(status_code=418, json_payload={"error": {"code": 418, "message": "I'm a teapot."}})
    error = HttpResponseError(response=response)
    command = mock.Mock(side_effect=error)
    polling_method = DeleteRecoverPollingMethod(command, final_resource=None, finished=False)

    with mock.patch(SLEEP, raise_exception("polling method shouldn't sleep after an unexpected error")):
        with pytest.raises(HttpResponseError):
            polling_method.run()

    assert command.call_count == 1

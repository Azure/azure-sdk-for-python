# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import functools
from typing import Any, Iterable, List
from azure.core.tracing.decorator import distributed_trace
from azure.health.deidentification.models import DeidentificationDocumentDetails, DeidentificationJob
from ._client import DeidentificationClient as DeidentificationClientGenerated
from ._utils import model_base as _model_base

__all__: List[str] = [
    "DeidentificationClient",
]  # Add all objects you want publicly available to users at this package level


class DeidentificationClient(DeidentificationClientGenerated):

    @distributed_trace
    def list_jobs(self, **kwargs: Any) -> Iterable[DeidentificationJob]:
        """
        List de-identification jobs.

        :return: An iterator like instance of DeidentificationJob
        :rtype: ~azure.core.paging.ItemPaged[~azure.health.deidentification.models.DeidentificationJob]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._list_jobs_internal(continuation_token_parameter=None, **kwargs)

    @distributed_trace
    def list_job_documents(self, job_name: str, **kwargs: Any) -> Iterable[DeidentificationDocumentDetails]:
        """
        List processed documents within a job.

        :param job_name: The name of a job. Required.
        :type job_name: str
        :return: An iterator like instance of DocumentDetails
        :rtype: ~azure.core.paging.ItemPaged[~azure.health.deidentification.models.DocumentDetails]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return super()._list_job_documents_internal(job_name=job_name, continuation_token_parameter=None, **kwargs)


_MISSING = object()
_IDENTITY_SHIM_MARKER = "_deid_preserves_container_identity"


def _preserve_container_identity() -> None:
    """Keep list/dict/set fields bound to one container across dict and property access.

    The generated ``_RestField.__get__`` stores a newly deserialized container back into
    ``_data``, detaching any container previously returned by ``model["field"]``, so later
    mutations through that reference are dropped on serialization. This wrapper copies the
    new contents into the original container and keeps it in ``_data``.

    TODO: remove once the emitter template is fixed (microsoft/typespec,
    packages/http-client-python/generator/pygen/codegen/templates/model_base.py.jinja2,
    ``_RestField.__get__``). See https://github.com/Azure/azure-sdk-for-python/pull/49627#discussion_r4342560283
    """
    rest_field_cls = _model_base._RestField  # pylint: disable=protected-access
    original_get: Any = rest_field_cls.__get__
    if getattr(original_get, _IDENTITY_SHIM_MARKER, False):
        return

    @functools.wraps(original_get)
    def __get__(self: Any, obj: Any, owner: Any = None) -> Any:
        if obj is None:
            return original_get(self, obj, owner)
        data = obj._data  # pylint: disable=protected-access
        name = self._rest_name  # pylint: disable=protected-access
        before = data.get(name, _MISSING)
        result = original_get(self, obj, owner)
        after = data.get(name, _MISSING)
        if before is after or result is not after:
            return result
        if isinstance(before, list) and isinstance(after, list):
            before[:] = after
        elif (isinstance(before, dict) and isinstance(after, dict)) or (
            isinstance(before, set) and isinstance(after, set)
        ):
            before.clear()
            before.update(after)
        else:
            return result
        data[name] = before
        return before

    setattr(__get__, _IDENTITY_SHIM_MARKER, True)
    setattr(rest_field_cls, "__get__", __get__)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    _preserve_container_identity()

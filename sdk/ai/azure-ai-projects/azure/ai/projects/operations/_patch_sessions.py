# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from pathlib import Path
from typing import Any
from azure.core.tracing.decorator import distributed_trace
from ._operations import BetaAgentsOperations as GeneratedBetaAgentsOperations
from .. import models as _models


class BetaAgentsOperations(GeneratedBetaAgentsOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta.agents` attribute.
    """

    @distributed_trace
    def upload_session_file(  # type: ignore[override]
        self,
        agent_name: str,
        session_id: str,
        content_or_file_path: "bytes | str",
        *,
        path: str,
        **kwargs: Any,
    ) -> _models.SessionFileWriteResult:
        """Upload a file to the session sandbox.

        Accepts either a ``bytes`` buffer or a local file path (``str``).
        When a file path is provided the file is read from disk and its contents
        are forwarded to the service. Maximum file size is 50 MB. Uploads
        exceeding this limit return 413 Payload Too Large.

        :param agent_name: The name of the agent. Required.
        :type agent_name: str
        :param session_id: The session ID. Required.
        :type session_id: str
        :param content_or_file_path: The binary content to upload, **or** the full path to a local
         file whose contents should be uploaded. Required.
        :type content_or_file_path: bytes or str
        :keyword path: The destination file path within the sandbox, relative to the session home
         directory. Required.
        :paramtype path: str
        :return: SessionFileWriteResult. The SessionFileWriteResult is compatible with
         MutableMapping
        :rtype: ~azure.ai.projects.models.SessionFileWriteResult
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises FileNotFoundError: If *content_or_file_path* is a ``str`` and the file does not exist.
        """
        if isinstance(content_or_file_path, str):

            file_path = Path(content_or_file_path)
            if not file_path.exists():
                raise ValueError(f"The provided file `{content_or_file_path}` does not exist.")
            if file_path.is_dir():
                raise ValueError(f"Provide a valid file path, not a folder path `{content_or_file_path}`.")

            with open(content_or_file_path, "rb") as f:
                content: bytes = f.read()
        else:
            content = content_or_file_path

        return super()._upload_session_file(agent_name, session_id, content, path=path, **kwargs)

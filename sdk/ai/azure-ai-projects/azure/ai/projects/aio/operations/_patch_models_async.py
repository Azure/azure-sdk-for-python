# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import os
from pathlib import Path
from typing import Any, Literal, Optional, Union, overload

from azure.core.exceptions import ResourceNotFoundError
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import BetaModelsOperations as BetaModelsOperationsGenerated
from ...models._models import (
    ModelPendingUploadRequest,
    ModelPendingUploadResponse,
    ModelVersion,
    PendingUploadType,
)

logger = logging.getLogger(__name__)


class BetaModelsOperations(BetaModelsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`beta.models <azure.ai.projects.aio.operations.BetaOperations.models>` attribute.
    """

    @staticmethod
    def _extract_pending_upload_targets(
        response: Union[ModelPendingUploadResponse, dict],
    ) -> "tuple[str, str, Optional[str]]":
        """Return ``(sas_uri, container_blob_uri, pending_upload_id)`` from a pending-upload response.

        The service currently returns the raw datastore-style payload
        (``blobReferenceForConsumption`` / ``temporaryDataReferenceId``) for some
        Foundry deployments rather than the SDK-modeled ``ModelPendingUploadResponse``
        shape (``blobReference`` / ``pendingUploadId``). Tolerate both wire
        shapes so callers don't have to.

        :param response: The pending-upload response from the service.
        :type response: ~azure.ai.projects.models.ModelPendingUploadResponse or dict
        :return: A tuple of ``(sas_uri, container_blob_uri, pending_upload_id)``.
        :rtype: tuple[str, str, str or None]
        """
        payload = dict(response) if isinstance(response, dict) else response.as_dict()

        blob_ref = payload.get("blobReferenceForConsumption") or payload.get("blobReference") or {}
        sas_uri = (blob_ref.get("credential") or {}).get("sasUri")
        container_blob_uri = blob_ref.get("blobUri")
        pending_upload_id = payload.get("temporaryDataReferenceId") or payload.get("pendingUploadId")

        if not sas_uri or not container_blob_uri:
            raise ValueError("Could not locate SAS URI / blob URI in pending_upload response: " f"{payload!r}")
        return sas_uri, container_blob_uri, pending_upload_id

    @staticmethod
    def _validate_create_inputs(
        *,
        name: str,
        version: str,
        source: Union[str, "os.PathLike[str]"],
        wait_for_commit: bool,
        polling_timeout: float,
        polling_interval: float,
    ) -> Path:
        """Validate ``create`` inputs up-front, before any service call.

        Returns the resolved ``Path`` for ``source``. Raises ``ValueError`` for
        bad inputs.

        :keyword name: Name of the model to register.
        :paramtype name: str
        :keyword version: Version identifier for the model.
        :paramtype version: str
        :keyword source: Local file or directory containing the model weights.
        :paramtype source: str or os.PathLike[str]
        :keyword wait_for_commit: Whether to poll for commit completion.
        :paramtype wait_for_commit: bool
        :keyword polling_timeout: Total seconds to poll for commit completion.
        :paramtype polling_timeout: float
        :keyword polling_interval: Seconds between poll attempts.
        :paramtype polling_interval: float
        :return: The resolved ``Path`` for ``source``.
        :rtype: pathlib.Path
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("`name` must be a non-empty string.")
        if not isinstance(version, str) or not version.strip():
            raise ValueError("`version` must be a non-empty string.")

        source_path = Path(os.fspath(source))
        if not source_path.exists():
            raise ValueError(f"Upload source does not exist: {source_path}")
        if source_path.is_dir() and not any(p.is_file() for p in source_path.rglob("*")):
            raise ValueError(f"Upload source directory is empty: {source_path}")
        if source_path.is_file() and source_path.stat().st_size == 0:
            raise ValueError(f"Upload source file is empty: {source_path}")

        if wait_for_commit:
            if polling_timeout <= 0:
                raise ValueError("`polling_timeout` must be > 0 when `wait_for_commit` is True.")
            if polling_interval <= 0:
                raise ValueError("`polling_interval` must be > 0 when `wait_for_commit` is True.")

        return source_path

    @staticmethod
    async def _upload_with_container_client(source: Path, sas_uri: str) -> None:
        """Upload ``source`` to the SAS container using ``azure.storage.blob.aio.ContainerClient``.

        :param source: Local file or directory to upload.
        :type source: pathlib.Path
        :param sas_uri: SAS URI for the destination container.
        :type sas_uri: str
        :raises RuntimeError: If ``azure-storage-blob`` is not installed.
        """
        try:
            from azure.storage.blob.aio import ContainerClient  # pylint: disable=import-outside-toplevel
        except ImportError as ex:
            raise RuntimeError(
                "`azure-storage-blob` is required for the async `create` helper. "
                "Install it with `pip install azure-storage-blob aiohttp`."
            ) from ex

        if source.is_dir():
            files = [p for p in source.rglob("*") if p.is_file()]
            if not files:
                raise ValueError(f"Upload source directory is empty: {source}")
        elif source.is_file():
            files = [source]
        else:
            raise ValueError(f"Upload source does not exist: {source}")

        # Don't log the SAS query string — it's a credential.
        redacted = sas_uri.split("?", 1)[0] + "?<sas-redacted>"
        logger.info("[create] uploading %d file(s) to %s", len(files), redacted)

        async with ContainerClient.from_container_url(sas_uri) as container_client:
            for f in files:
                rel = f.relative_to(source).as_posix() if source.is_dir() else f.name
                with f.open("rb") as fp:
                    await container_client.upload_blob(name=rel, data=fp, overwrite=True)
                logger.debug("[create] uploaded %s (%d bytes)", rel, f.stat().st_size)

    @overload
    async def create(
        self,
        *,
        name: str,
        version: str,
        source: Union[str, "os.PathLike[str]"],
        weight_type: Optional[str] = None,
        base_model: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional["dict[str, str]"] = None,
        wait_for_commit: Literal[True] = True,
        polling_timeout: float = 300.0,
        polling_interval: float = 2.0,
        **kwargs: Any,
    ) -> ModelVersion: ...

    @overload
    async def create(
        self,
        *,
        name: str,
        version: str,
        source: Union[str, "os.PathLike[str]"],
        weight_type: Optional[str] = None,
        base_model: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional["dict[str, str]"] = None,
        wait_for_commit: Literal[False],
        polling_timeout: float = 300.0,
        polling_interval: float = 2.0,
        **kwargs: Any,
    ) -> None: ...

    @distributed_trace_async
    async def create(
        self,
        *,
        name: str,
        version: str,
        source: Union[str, "os.PathLike[str]"],
        weight_type: Optional[str] = None,
        base_model: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional["dict[str, str]"] = None,
        wait_for_commit: bool = True,
        polling_timeout: float = 300.0,
        polling_interval: float = 2.0,
        **kwargs: Any,
    ) -> Optional[ModelVersion]:
        """Register a local model by running the full upload-first sequence (async).

        This wraps the three mandatory steps of the model-registration spec
        into a single call:

        1. :meth:`pending_upload` — provision a project-managed blob container
           and obtain a SAS URI.
        2. Upload the local weight files to the SAS container using
           :class:`azure.storage.blob.aio.ContainerClient`.
        3. :meth:`pending_create_version` — finalize registration with the
           ``ModelVersion`` body (``blob_uri``, ``weight_type``, ``base_model``,
           ``description``, ``tags``).

        Requires the ``azure-storage-blob`` package (with ``aiohttp``) for the
        upload step.

        :keyword name: Name of the model to register. Required.
        :paramtype name: str
        :keyword version: Version identifier for the model. Required.
        :paramtype version: str
        :keyword source: Local file or directory containing the model weights.
            If a directory, its contents are uploaded recursively to the SAS
            container root. Required.
        :paramtype source: str or os.PathLike[str]
        :keyword weight_type: Optional weight type (e.g. ``"FullWeight"``,
            ``"LoRA"``, ``"DraftModel"``).
        :paramtype weight_type: str
        :keyword base_model: Optional base model asset ID.
        :paramtype base_model: str
        :keyword description: Optional asset description.
        :paramtype description: str
        :keyword tags: Optional asset tags.
        :paramtype tags: dict[str, str]
        :keyword wait_for_commit: When True (default) poll :meth:`get` until
            the committed ``ModelVersion`` is observable, and return it.
            When False, return ``None`` after the async commit is accepted.
        :paramtype wait_for_commit: bool
        :keyword polling_timeout: Total seconds to poll for commit completion.
        :paramtype polling_timeout: float
        :keyword polling_interval: Seconds between poll attempts.
        :paramtype polling_interval: float
        :return: The committed :class:`~azure.ai.projects.models.ModelVersion`
            when ``wait_for_commit`` is True, otherwise ``None``.
        :rtype: ~azure.ai.projects.models.ModelVersion or None
        :raises ValueError: If ``name``/``version`` are empty, ``source`` does
            not exist or is empty, polling parameters are non-positive, or the
            pending-upload response is missing the SAS / blob URI.
        :raises RuntimeError: If ``azure-storage-blob`` is not installed or
            the registration does not commit before ``polling_timeout`` elapses.
        """
        # --- Step 0: validate inputs up-front --------------------------------
        source_path = self._validate_create_inputs(
            name=name,
            version=version,
            source=source,
            wait_for_commit=wait_for_commit,
            polling_timeout=polling_timeout,
            polling_interval=polling_interval,
        )

        # --- Step 1: StartPendingUpload --------------------------------------
        logger.info(
            "[create] step 1/3 pending_upload(name=%r, version=%r)",
            name,
            version,
        )
        pending = await self.pending_upload(
            name=name,
            version=version,
            pending_upload_request=ModelPendingUploadRequest(
                pending_upload_type=PendingUploadType.TEMPORARY_BLOB_REFERENCE,
            ),
            **kwargs,
        )
        sas_uri, container_blob_uri, pending_upload_id = self._extract_pending_upload_targets(pending)
        logger.info(
            "[create] pending_upload_id=%s blob_uri=%s",
            pending_upload_id,
            container_blob_uri,
        )

        # --- Step 2: Upload via async ContainerClient ------------------------
        logger.info("[create] step 2/3 async upload from %s", source_path)
        await self._upload_with_container_client(source_path, sas_uri)

        # --- Step 3: Commit registration -------------------------------------
        model_version_body = ModelVersion(
            blob_uri=container_blob_uri,
            weight_type=weight_type,
            base_model=base_model,
            description=description,
            tags=tags or {},
        )
        logger.info(
            "[create] step 3/3 pending_create_version(name=%r, version=%r)",
            name,
            version,
        )
        await self.pending_create_version(name=name, version=version, model_version=model_version_body, **kwargs)

        if not wait_for_commit:
            return None

        # The async op returns 202; the service materializes the ModelVersion
        # asynchronously. Poll get() until it appears or we time out.
        import time  # pylint: disable=import-outside-toplevel

        deadline = time.monotonic() + polling_timeout
        last_exc: Optional[BaseException] = None
        while True:
            try:
                return await self.get(name=name, version=version, **kwargs)
            except ResourceNotFoundError as ex:
                last_exc = ex
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        f"Model {name!r}@{version!r} did not appear within "
                        f"{polling_timeout}s after pending_create_version."
                    ) from last_exc
                await asyncio.sleep(polling_interval)


__all__ = ["BetaModelsOperations"]

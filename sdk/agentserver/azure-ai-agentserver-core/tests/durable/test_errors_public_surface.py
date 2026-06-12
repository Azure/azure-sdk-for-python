# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 019 Area D — Developer-facing error rename + prefix dispatch
(FR-D-001..004, SC-9b, SC-11).

Verifies:

- ``OutputTooLarge`` is exported from
  ``azure.ai.agentserver.core.durable`` (FR-D-001).
- ``AttachmentTooLarge`` and ``AttachmentLimitExceeded`` are NOT
  public (FR-D-002 / FR-D-003) — importing them by their old names
  raises ``ImportError`` and they do not appear in ``__all__``
  (SC-11).
- The framework's prefix-dispatch wrapper translates the internal
  ``_AttachmentTooLarge`` raised against a known attachment-key
  prefix into the right developer-facing exception:

  - ``_input`` → ``InputTooLarge`` (FR-D-004)
  - ``_steering_input_<seq>`` → ``InputTooLarge`` (FR-D-004 / SC-9b)
  - ``_output`` → ``OutputTooLarge`` (FR-D-004)

Reference: docs/task-and-streaming-spec.md §23.7, §39, §59 C-ATT-4.
"""

from __future__ import annotations

import importlib

import pytest


# --------------------------------------------------------------------- #
# FR-D-001 — OutputTooLarge is a public exception
# --------------------------------------------------------------------- #


def test_output_too_large_is_public() -> None:
    """FR-D-001 / SC-9 — ``OutputTooLarge`` MUST be importable from
    the public ``azure.ai.agentserver.core.durable`` surface and MUST
    inherit ``ValueError``.
    """
    from azure.ai.agentserver.core.durable import OutputTooLarge

    assert issubclass(OutputTooLarge, ValueError), (
        "OutputTooLarge MUST be a ValueError subclass per FR-D-001"
    )
    # Must accept the documented constructor shape.
    exc = OutputTooLarge(task_id="t", size_bytes=3_000_000, max_bytes=2_097_152)
    assert exc.task_id == "t"
    assert exc.size_bytes == 3_000_000
    assert exc.max_bytes == 2_097_152


# --------------------------------------------------------------------- #
# FR-D-002 / FR-D-003 / SC-11 — attachment-vocabulary errors are internal
# --------------------------------------------------------------------- #


def test_attachment_too_large_not_public() -> None:
    """FR-D-002 / SC-11 — ``AttachmentTooLarge`` MUST be absent from
    the public surface; ``from durable import AttachmentTooLarge``
    raises ``ImportError``.
    """
    mod = importlib.import_module("azure.ai.agentserver.core.durable")
    assert "AttachmentTooLarge" not in (mod.__all__ or ()), (
        "AttachmentTooLarge must NOT appear in durable.__all__ "
        "(FR-D-002). Attachments are a framework concept that "
        "developers never name."
    )
    with pytest.raises(ImportError):
        # Force a clean ImportError on the explicit name.
        exec(
            "from azure.ai.agentserver.core.durable import AttachmentTooLarge",
            {},
        )


def test_attachment_limit_exceeded_not_public() -> None:
    """FR-D-003 / SC-11 — same rule for ``AttachmentLimitExceeded``.
    """
    mod = importlib.import_module("azure.ai.agentserver.core.durable")
    assert "AttachmentLimitExceeded" not in (mod.__all__ or ()), (
        "AttachmentLimitExceeded must NOT appear in durable.__all__ "
        "(FR-D-003)."
    )
    with pytest.raises(ImportError):
        exec(
            "from azure.ai.agentserver.core.durable import AttachmentLimitExceeded",
            {},
        )


# --------------------------------------------------------------------- #
# FR-D-004 — framework re-raises by attachment-key prefix
# --------------------------------------------------------------------- #


def _internal_attachment_too_large_cls():
    """Locate the internal ``_AttachmentTooLarge`` exception class.

    Spec 019 FR-D-002 says the rename target is
    ``_AttachmentTooLarge`` (leading underscore). Implementation
    detail; tests reach into ``_exceptions`` for the rename.
    """
    mod = importlib.import_module("azure.ai.agentserver.core.durable._exceptions")
    return getattr(mod, "_AttachmentTooLarge")


def test_input_too_large_remap_from_internal_input_key() -> None:
    """FR-D-004 — when the framework's prefix dispatcher receives an
    internal ``_AttachmentTooLarge`` raised against attachment key
    ``_input``, it MUST re-raise the developer-facing ``InputTooLarge``.

    Implementation detail: the dispatcher is exposed as a module-level
    helper (``_attachments_error_to_developer_facing`` or equivalent
    name); tests look it up by either name.
    """
    from azure.ai.agentserver.core.durable import InputTooLarge

    internal_cls = _internal_attachment_too_large_cls()
    mod = importlib.import_module("azure.ai.agentserver.core.durable._attachments")
    dispatcher = (
        getattr(mod, "_remap_attachment_error", None)
        or getattr(mod, "_attachments_error_to_developer_facing", None)
        or getattr(mod, "_remap_attachment_too_large", None)
    )
    assert dispatcher is not None, (
        "no prefix dispatcher helper found in _attachments.py; "
        "FR-D-004 requires a single module-level helper that maps "
        "internal _AttachmentTooLarge to the developer-facing error."
    )

    internal = internal_cls(
        task_id="t", attachment_key="_input", size_bytes=3_000_000, max_bytes=2_097_152
    )
    with pytest.raises(InputTooLarge) as excinfo:
        raise dispatcher(internal)
    assert excinfo.value.task_id == "t"
    assert excinfo.value.size_bytes == 3_000_000


def test_input_too_large_remap_from_steering_key() -> None:
    """FR-D-004 / SC-9b — when the framework receives the internal
    ``_AttachmentTooLarge`` for a ``_steering_input_<seq>`` key, it
    MUST re-raise ``InputTooLarge`` (NOT a steering-specific type).
    The prefix dispatcher treats ``_input`` and ``_steering_input_*``
    uniformly because both are caller-supplied inputs at the
    developer's layer.
    """
    from azure.ai.agentserver.core.durable import InputTooLarge

    internal_cls = _internal_attachment_too_large_cls()
    mod = importlib.import_module("azure.ai.agentserver.core.durable._attachments")
    dispatcher = (
        getattr(mod, "_remap_attachment_error", None)
        or getattr(mod, "_attachments_error_to_developer_facing", None)
        or getattr(mod, "_remap_attachment_too_large", None)
    )
    assert dispatcher is not None

    internal = internal_cls(
        task_id="t",
        attachment_key="_steering_input_3",
        size_bytes=3_000_000,
        max_bytes=2_097_152,
    )
    with pytest.raises(InputTooLarge):
        raise dispatcher(internal)


def test_output_too_large_remap_from_internal_output_key() -> None:
    """FR-D-004 — for the ``_output`` attachment key, the prefix
    dispatcher MUST re-raise ``OutputTooLarge``.
    """
    from azure.ai.agentserver.core.durable import OutputTooLarge

    internal_cls = _internal_attachment_too_large_cls()
    mod = importlib.import_module("azure.ai.agentserver.core.durable._attachments")
    dispatcher = (
        getattr(mod, "_remap_attachment_error", None)
        or getattr(mod, "_attachments_error_to_developer_facing", None)
        or getattr(mod, "_remap_attachment_too_large", None)
    )
    assert dispatcher is not None

    internal = internal_cls(
        task_id="t", attachment_key="_output", size_bytes=3_000_000, max_bytes=2_097_152
    )
    with pytest.raises(OutputTooLarge) as excinfo:
        raise dispatcher(internal)
    assert excinfo.value.task_id == "t"
    assert excinfo.value.size_bytes == 3_000_000


# ===========================================================================
# Spec 020 — Workstream C: no new public exports from the parity work
# ===========================================================================


def test_hosted_conflict_is_not_public() -> None:
    """C-ERR-4: `_HostedConflict` MUST NOT be in the public exception surface.

    It is an internal discriminator the framework's response classifier
    raises so lifecycle code can branch on the service's distinct error
    codes (task_immutable, lease_held_by_another, etag_mismatch, ...).
    The developer never imports it, catches it, or sees its name.
    """
    import azure.ai.agentserver.core.durable as pub

    assert not hasattr(pub, "_HostedConflict"), (
        "_HostedConflict is internal; it MUST NOT be exported via the "
        "public `durable` namespace."
    )
    assert "_HostedConflict" not in getattr(pub, "__all__", []), (
        "_HostedConflict must not appear in __all__."
    )


def test_no_service_code_strings_as_public_type_names() -> None:
    """C-ERR-5: service error code strings must NOT appear as public type names.

    The service emits codes like 'task_immutable', 'lease_held_by_another',
    etc. These are internal dispatch keys only; no developer-facing Python
    class should be named after them.
    """
    import azure.ai.agentserver.core.durable as pub

    service_code_camel_cases = {
        "TaskImmutable",
        "InvalidStateTransition",
        "LeaseHeldByAnother",
        "TaskAlreadyExists",
        "LeaseOwnershipChanged",
        "EtagMismatch",
    }
    for name in service_code_camel_cases:
        assert not hasattr(pub, name), (
            f"{name!r} must not be exported from the public durable namespace "
            f"— service codes belong to internal dispatch only."
        )

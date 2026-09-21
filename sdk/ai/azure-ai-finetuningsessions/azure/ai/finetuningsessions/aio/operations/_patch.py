# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Keep earlier async operation keywords working across regeneration."""
    from ..._compat import patch_operation_keywords
    from ..._legacy_polling import install_legacy_pollers
    from . import _operations

    patch_operation_keywords(_operations.SessionsOperations, {"create": {"body": "session"}})
    patch_operation_keywords(
        _operations.TrainingOperations,
        {name: {"body": "request"} for name in ("forward_backward", "forward", "optimizer_step")},
    )
    patch_operation_keywords(
        _operations.CheckpointsOperations,
        {name: {"body": "checkpoint"} for name in ("save", "save_sampler_weights")},
    )
    patch_operation_keywords(_operations.SamplingOperations, {"sample": {"body": "sample"}})
    patch_operation_keywords(_operations.Operations, {"get": {"operation_id": "request_id_parameter"}})

    install_legacy_pollers(
        _operations.SessionsOperations,
        {"begin_create": ("create", "create_session"), "begin_unload": ("unload", "unload_session")},
        asynchronous=True,
    )
    install_legacy_pollers(
        _operations.TrainingOperations,
        {
            "begin_forward_backward": ("forward_backward", "forward_backward"),
            "begin_optim_step": ("optimizer_step", "optim_step"),
        },
        asynchronous=True,
    )
    install_legacy_pollers(
        _operations.CheckpointsOperations,
        {
            "begin_save": ("save", "save_checkpoint"),
            "begin_save_sampler_weights": ("save_sampler_weights", "save_sampler_weights"),
        },
        asynchronous=True,
    )
    install_legacy_pollers(_operations.SamplingOperations, {"begin_sample": ("sample", "sample")}, asynchronous=True)

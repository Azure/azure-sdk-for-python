# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builder for a pipeline job (smoke serialization suite).

The pipeline envelope (``JobBase`` with ``PipelineJob`` properties) and its node subtree were migrated
to ``arm_ml_service`` together with the shared job boundary (``_input_output_helpers``, the DSL node
serializer ``get_rest_dict_for_node_attrs``, etc.). This pins the full pipeline request body -- the
envelope plus the serialized node graph -- byte-for-byte against the pre-migration baseline.

The pipeline is loaded from ``_pipeline_smoke.yml`` whose nodes reference REGISTERED components by ARM
id (no inline/anonymous components), so ``_to_rest_object()`` serializes cleanly offline without a
client to resolve component ids and without any mocking (inline components only stringify at real
submit time). ``load_job`` is the real public loader -- no test doubles.
"""
import os

from azure.ai.ml import load_job

_THIS_DIR = os.path.dirname(__file__)


def build_pipeline_job_registry_components():
    """PipelineJob with two registry-component nodes, pipeline inputs, tags and settings."""
    return load_job(os.path.join(_THIS_DIR, "_pipeline_smoke.yml"))


PIPELINE_BUILDERS = {
    "pipeline_job_registry_components": build_pipeline_job_registry_components,
}

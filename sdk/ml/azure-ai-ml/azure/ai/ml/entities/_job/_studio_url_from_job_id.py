# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from typing import Optional

from azure.ai.ml._azure_environments import _get_aml_resource_id_from_metadata, _get_default_cloud_name

JOB_ID_RE_PATTERN = re.compile(
    (
        r"\/subscriptions\/(?P<subscription>[\w,-]+)\/resourceGroups\/(?P<resource_group>[\w,-]+)\/providers"
        r"\/Microsoft\.MachineLearningServices\/workspaces\/(?P<workspace>[\w,-]+)\/jobs\/(?P<run_id>[\w,-]+)"
    )  # fmt: skip
)


def studio_url_from_job_id(job_id: str) -> Optional[str]:
    resource_id = _get_aml_resource_id_from_metadata(_get_default_cloud_name())
    m = JOB_ID_RE_PATTERN.match(job_id)
    if m:
        return (
            f"{resource_id}/runs/{m.group('run_id')}?wsid=/subscriptions/{m.group('subscription')}"
            f"/resourcegroups/{m.group('resource_group')}/workspaces/{m.group('workspace')}"
        )  # fmt: skip
    return None

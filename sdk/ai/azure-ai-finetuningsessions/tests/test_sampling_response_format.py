import json

from azure.ai.finetuningsessions._patch import _SdkJSONEncoder
from azure.ai.finetuningsessions.models import SamplingParams


def test_sampling_params_serializes_response_format() -> None:
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "Answer",
            "schema": {
                "type": "object",
                "properties": {"answer": {"type": "string"}},
                "required": ["answer"],
            },
            "strict": True,
        },
    }

    sampling_params = SamplingParams(
        max_tokens=16,
        temperature=1.0,
        top_p=1.0,
        top_k=-1,
        response_format=response_format,
    )

    payload = json.loads(json.dumps(sampling_params, cls=_SdkJSONEncoder, exclude_readonly=True))

    assert payload["response_format"] == response_format

# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

evaluator_to_data_source_config = {
    "coherence": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "response": {"type": "string"}},
            "required": ["query", "response"],
        },
        "include_sample_schema": True,
    },
    "fluency": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "response": {"type": "string"}},
            "required": ["response"],
        },
        "include_sample_schema": True,
    },
    "groundedness": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "context": {"type": "string"},
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {
                    "anyOf": [{"type": "string"}, {"type": "object"}, {"type": "array", "items": {"type": "object"}}]
                },
            },
            "required": ["response"],
        },
        "include_sample_schema": True,
    },
    "intent_resolution": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["query", "response"],
        },
        "include_sample_schema": True,
    },
    "relevance": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "response": {"type": "string"}},
            "required": ["query", "response"],
        },
        "include_sample_schema": True,
    },
    "response_completeness": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"ground_truth": {"type": "string"}, "response": {"type": "string"}},
            "required": ["ground_truth", "response"],
        },
        "include_sample_schema": True,
    },
    "task_adherence": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["query", "response"],
        },
        "include_sample_schema": True,
    },
    "task_completion": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["query", "response"],
        },
        "include_sample_schema": True,
    },
    "tool_call_accuracy": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_calls": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["query", "tool_definitions"],
        },
        "include_sample_schema": True,
    },
    "tool_input_accuracy": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["query", "response", "tool_definitions"],
        },
        "include_sample_schema": True,
    },
    "tool_output_utilization": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["query", "response"],
        },
        "include_sample_schema": True,
    },
    "tool_selection": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_calls": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["query", "response", "tool_definitions"],
        },
        "include_sample_schema": True,
    },
    "tool_success": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "tool_definitions": {"anyOf": [{"type": "object"}, {"type": "array", "items": {"type": "object"}}]},
                "response": {"anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "object"}}]},
            },
            "required": ["response"],
        },
        "include_sample_schema": True,
    },
}

evaluator_to_data_mapping = {
    "coherence": {"query": "{{item.query}}", "response": "{{item.response}}"},
    "fluency": {"query": "{{item.query}}", "response": "{{item.response}}"},
    "groundedness": {
        "context": "{{item.context}}",
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_definitions": "{{item.tool_definitions}}",
    },
    "intent_resolution": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_definitions": "{{item.tool_definitions}}",
    },
    "relevance": {"query": "{{item.query}}", "response": "{{item.response}}"},
    "response_completeness": {"ground_truth": "{{item.ground_truth}}", "response": "{{item.response}}"},
    "task_adherence": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_definitions": "{{item.tool_definitions}}",
    },
    "task_completion": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_definitions": "{{item.tool_definitions}}",
    },
    "tool_call_accuracy": {
        "query": "{{item.query}}",
        "tool_definitions": "{{item.tool_definitions}}",
        "tool_calls": "{{item.tool_calls}}",
        "response": "{{item.response}}",
    },
    "tool_input_accuracy": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_definitions": "{{item.tool_definitions}}",
    },
    "tool_output_utilization": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_definitions": "{{item.tool_definitions}}",
    },
    "tool_selection": {
        "query": "{{item.query}}",
        "response": "{{item.response}}",
        "tool_calls": "{{item.tool_calls}}",
        "tool_definitions": "{{item.tool_definitions}}",
    },
    "tool_success": {"tool_definitions": "{{item.tool_definitions}}", "response": "{{item.response}}"},
}

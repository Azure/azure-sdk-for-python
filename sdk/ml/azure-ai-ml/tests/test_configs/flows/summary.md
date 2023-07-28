# Summary of preferred solution

- support load from `flow.dag.yaml` or `run.yaml` (referring a `flow.dag.yaml`)
- no `flow.meta.yaml`
- no `flow_component.yaml`

fields:
- name: `load_component(name=xxx)` > `flow.dag.yaml` > `run.yaml:name`
- version: `load_component(version=xxx)` > auto-generated (hash for anonymous and auto-increment for named)
- display_name/description/properties/tags: `load_component(params_override=xxx)` > `run.yaml:xxx` > `flow.dag.yaml:xxx`
- inputs.columns_mapping_key.default: `run.yaml:columns_mapping:xxx` > `flow.dag.yaml:inputs:xxx:default`
- inputs.columns_mapping_key.description: do not support setting this
- inputs.connections.node_name.connection_name/deployment_name.default: `run.yaml:connections:node_name:connection_name/deployment_name`
- inputs.connections.node_name.connection_name/deployment_name.description: do not support setting this
- variant: `run.yaml:variant` or default variant in `flow.dag.yaml`
- runtime: `run.yaml:runtime` or require user to generate a `flow.tools.json` and avoid ignoring it
- additional_includes: `flow.dag.yaml:additional_includes`
- is_deterministic: default to `True` and allow to overwrite by load_component(params_override=xxx)
- task.environment: build from `flow.dag.yaml:environment`
- code: parent of `flow.dag.yaml`
- environment_variables: `run.yaml:environment_variables`

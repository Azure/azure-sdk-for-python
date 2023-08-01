# Flow in Pipeline experience proposal

## Background

After customer finalized a flow in prompt-flow, they may want to integrate it with existing pipeline. So we need to provide customer a way to use flow along with pipeline job in azure-ai-ml.

### Goal

+ customer can refer to flow as a component in pipeline job in azure-ai-ml
  + it should include both CLI & SDK experience
+ need to leave an interface to specify component type
  + 1p customers need to refer a flow as a parallel component for acceleration
  + PM has used command component for public review as it's easier to understand

### Non-goal

+ direct referral from sources other than code-first experience won't be discussed here
  + like drag a flow to a pipeline job in UX
  + we'll always assume that customer has a code-first flow definition
+ detailed samples for features like side input

## Related Files & Concepts

- `flow.dag.yaml`: flow diagram definition yaml
- `run.yaml`: run config for a flow run, will refer to `flow.dag.yaml`
- `flow.meta.yaml`: include meta information for a flow. We don't have this in code-first experience for now.
- `flow.component.yaml`: include all potential gap fields between a flow and its corresponding component. We don't have this in code-first experience for now.

## Proposal Summary

- support directly call `load_component` from a `flow.dag.yaml`

  - SDK experience:

  ```python
  from azure.ai.ml import load_component
  from azure.ai.ml import dsl
  
  flow_component = load_component("../flow/flow.dag.yaml")
  
  @dsl.pipeline
  def pipeline_with_flow(job_input):
      flow_node = flow_component(data=job_input)
      flow_node.logging_level = "DEBUG"
      return {"job_output": flow_node.outputs.flow_outputs}
  ```

  - CLI experience

  ```yaml
  type: pipeline
  inputs:
    job_input:
      type: uri_folder
      path: "../test_data/flow_input_data.jsonl"
  jobs:
    flow_node:
      component: ../flow/flow.dag.yaml
      type: parallel
      logging_level: DEBUG
  ```

  + more details in [pipeline_with_flow.yaml](../pipeline_job/pipeline_with_flow.yaml)

- also support load from `run.yaml` (referring a `flow.dag.yaml`)

  - `run.yaml` is part of prompt-flow code-first experience
  - there is a significant overlap between `run.yaml` and what we need to build a component

- no `flow.meta.yaml`
  - we want to support load from a `run.yaml`, while `run.yaml` won't refer `flow.meta.yaml`
- no `flow_component.yaml`
  - this component spec will have fixed inputs/outputs which we want to be transparent for customers
  - most necessary attributes are already in `flow.dag.yaml` or `run.yaml`

### Fields Details

1. the table cell will be the dot key of corresponding attribute; will fill with `-` if not supported
2. fields will always load wit priority: `load_component` > `run.yaml` > `flag.dag.yaml` > `default value`

| Field Name                                                   | load_component                   | run.yaml                                           | flow.dag.yaml                                            | default value                                                | comment                                                      |
| ------------------------------------------------------------ | -------------------------------- | -------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Run Blocker**                                              |                                  |                                                    |                                                          |                                                              |                                                              |
| type                                                         | type                             | -                                                  | -                                                        | parallel                                                     | can be inferred from `node.type` in `pipeline.yaml`; **`type` is not a valid param for `load_component` on regular components** |
| additional_includes                                          | -                                | -                                                  | additional_includes                                      | -                                                            | **v2 sdk need to understand the addtional_includes in dag.yaml to build code snapshot** |
| variant                                                      | -                                | variant                                            | -                                                        | -                                                            |                                                              |
|                                                              |                                  |                                                    |                                                          |                                                              |                                                              |
| task.environment/environment                                 | -                                | -                                                  | environment                                              | latest public prompt-flow runtime image                      |                                                              |
| is_deterministic                                             | params_override.is_deterministic | -                                                  | -                                                        | True                                                         |                                                              |
| code                                                         | -                                | -                                                  | -                                                        | parent of `flow.dag.yaml`                                    |                                                              |
| **Better to have**                                           |                                  |                                                    |                                                          |                                                              |                                                              |
| name (display on UX)                                         | name                             | name                                               | name                                                     | azureml_anonymous                                            |                                                              |
| version                                                      | version                          | -                                                  | -                                                        | hash value if name is not provided; auto-increment if name is provided; raise exception if auto-increment failed | `version` must be provided along with `name`                 |
| display_name                                                 | params_override.display_name     | display_name                                       | display_name                                             | -                                                            |                                                              |
| description                                                  | params_override.description      | description                                        | description                                              | -                                                            |                                                              |
| properties                                                   | params_override.properties       | properties                                         | properties                                               | -                                                            |                                                              |
| tags                                                         | params_override.tags             | tags                                               | tags                                                     | -                                                            |                                                              |
| inputs.<input_name>.default                                  | -                                | columns_mapping.<input_name>                       | inputs.<input_name>.default                              | -                                                            |                                                              |
| inputs.<input_name>.description                              | -                                | -                                                  | inputs.<input_name>.description                          | -                                                            |                                                              |
| inputs.connections.<node_name>.connection/deployment_name.default | -                                | connections.<node_name>.connection/deployment_name | nodes.<node_name>.connection/deployment_name.default     | -                                                            |                                                              |
| inputs.connections.<node_name>.connection/deployment_name.description | -                                | -                                                  | nodes.<node_name>.connection/deployment_name.description | -                                                            |                                                              |
| **Need to discuss**                                          |                                  |                                                    |                                                          |                                                              |                                                              |
| runtime                                                      | -                                | runtime                                            | -                                                        | -                                                            | will raise exception if runtime is not provided and no `flow.tools.json` is under flow directory |

### Changes Needed

1. Need to update `load_component`
   1. may need to add a private parameter `type` for `load_component`
   2. it will take some effort
2. Need to check if we have supported specifying `environment_variable` in parallel component
3. Need to add below fields to `flow.dag.yaml` (it's also an option not to support setting them via `flow.dag.yaml`)
   1. name
   2. display_name
   3. description
   4. properties
   5. tags

## Open Questions

1. `name` for flow component in anonymous usage
   1. option 1: always use `name` provided by `flow.dag.yaml` or `run.yaml` in component creation
   2. option 2: display `name` provided by `flow.dag.yaml` or `run.yaml` in UX, but only use them to register the component when explicitly calling `ml_client.components.create_or_update` or `az ml component create`; Use anonymous name and hash version for component registration in other cases
      1. this is more align with behavior of v2 regular components
      2. this required a MT change

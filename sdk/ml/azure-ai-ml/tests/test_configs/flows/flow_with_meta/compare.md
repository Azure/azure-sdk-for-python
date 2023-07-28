| field name          | can be ignore? | flow.dag.yaml                                 | flow.meta.yaml                                 | run.yaml                     | standalone file       |
| ------------------- | -------------- | --------------------------------------------- | ---------------------------------------------- | ---------------------------- | --------------------- |
| additional_includes | N              | Y - part of flow definition                   | N - it's not meta                              | N - it's shared by all runs  | ? - not align with v2 |
| name                | ?              | ? - conflict with UX?                         | Y                                              | ? - it's shared by all runs? | N                     |
| version             | Y              | ?                                             | ? - do we have concept version for flow in UX? | N                            | N                     |
| display_name        | ?              | ?                                             | Y                                              | N - not a run config?        | N                     |
| tags                | ?              | ?                                             | ? - do we have concept tags for flow in UX?    | N - not a run config?        | N                     |
| runtime             | ?              | N - not part of flow definition               | N - not meta?                                  | Y                            | N                     |
| node_variant        | ?              | N - not part of flow definition               | N - not meta?                                  | Y                            | N                     |
| columns_mapping     | Y              | N - not part of flow definition               | N - not meta?                                  | Y                            | N                     |
| connections         | Y              | N - not part of flow definition               | N - not meta?                                  | Y                            | N                     |
| is_deterministic    | Y              | N - we don't have such concept in promptflow? | N                                              | N                            | N                     |

conclusion:

| filed name          | place                                                        |
| ------------------- | ------------------------------------------------------------ |
| additional_includes | flow.dag.yaml                                                |
| name                | flow.dag.yaml/ignore(can be passed via public interface of `load_component`) |
| version             | ignore                                                       |
| display_name        | the same to `name`                                           |
| tags                | the same to `name`                                           |
| runtime             | run.yaml                                                     |
| node_variant        | run.yaml                                                     |
| columns_mapping     | run.yaml                                                     |
| connections         | run.yaml                                                     |
| is_deterministic    | ignore (can be passed via private interface of `load_component`) |

can either be load from a `flow.dag.yaml` or a `run.yaml`. Will respect information from `run.yaml` if load from it. 
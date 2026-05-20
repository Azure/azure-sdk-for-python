# AIProjectClient Subclients

This document lists all sub-clients available on `AIProjectClient` and their public method counts. Overload methods are not counted. Only synchronous methods are counted (but each one has an equivalent asynchronous method).


## Top-level Sub-clients

| Subclient | Class Name | Public Methods |
|-----------|------------|----------------|
| `agents` | AgentsOperations | 8 |
| `evaluation_rules` | EvaluationRulesOperations | 4 |
| `connections` | ConnectionsOperations | 3 |
| `datasets` | DatasetsOperations | 9 |
| `deployments` | DeploymentsOperations | 2 |
| `indexes` | IndexesOperations | 5 |
| `telemetry` | TelemetryOperations | 1 |
| `beta` | BetaOperations | 0 (container only) |

## Nested Sub-clients on `.beta`

| Subclient | Class Name | Public Methods |
|-----------|------------|----------------|
| `beta.agents` | BetaAgentsOperations | 21 |
| `beta.datasets` | BetaDatasetsOperations | 5 |
| `beta.evaluation_taxonomies` | BetaEvaluationTaxonomiesOperations | 5 |
| `beta.evaluators` | BetaEvaluatorsOperations | 13 |
| `beta.insights` | BetaInsightsOperations | 3 |
| `beta.memory_stores` | BetaMemoryStoresOperations | 13 |
| `beta.models` | BetaModelsOperations | 8 |
| `beta.red_teams` | BetaRedTeamsOperations | 3 |
| `beta.routines` | BetaRoutinesOperations | 8 |
| `beta.schedules` | BetaSchedulesOperations | 6 |
| `beta.skills` | BetaSkillsOperations | 7 |
| `beta.toolboxes` | BetaToolboxesOperations | 8 |

## Summary

**Total: 132 unique public methods across all subclients**

---

### Method Details

#### AgentsOperations (8)
`get`, `delete`, `list`, `create_version`, `create_version_from_manifest`, `get_version`, `delete_version`, `list_versions`

#### EvaluationRulesOperations (4)
`get`, `delete`, `create_or_update`, `list`

#### ConnectionsOperations (3)
`get`, `get_default`, `list`

#### DatasetsOperations (9)
`list_versions`, `list`, `get`, `delete`, `create_or_update`, `pending_upload`, `get_credentials`, `upload_file`, `upload_folder`

#### DeploymentsOperations (2)
`get`, `list`

#### IndexesOperations (5)
`list_versions`, `list`, `get`, `delete`, `create_or_update`

#### TelemetryOperations (1)
`get_application_insights_connection_string`

#### BetaAgentsOperations (21)
`patch_agent_details`, `create_version_from_code`, `download_agent_code`, `create_session`, `get_session`, `delete_session`, `list_sessions`, `get_session_log_stream`, `upload_session_file`, `download_session_file`, `get_session_files`, `delete_session_file`, `create_optimization_job`, `get_optimization_job`, `list_optimization_jobs`, `cancel_optimization_job`, `delete_optimization_job`, `list_optimization_candidates`, `get_optimization_candidate`, `get_optimization_candidate_config`, `get_optimization_candidate_results`

#### BetaDatasetsOperations (5)
`cancel_generation_job`, `create_generation_job`, `delete_generation_job`, `get_generation_job`, `list_generation_jobs`

#### BetaEvaluationTaxonomiesOperations (5)
`create`, `delete`, `get`, `list`, `update`

#### BetaEvaluatorsOperations (13)
`cancel_generation_job`, `create_generation_job`, `create_version`, `delete_generation_job`, `delete_version`, `get_credentials`, `get_generation_job`, `get_version`, `list`, `list_generation_jobs`, `list_versions`, `pending_upload`, `update_version`

#### BetaInsightsOperations (3)
`generate`, `get`, `list`

#### BetaMemoryStoresOperations (13)
`begin_update_memories`, `create`, `create_memory`, `delete`, `delete_memory`, `delete_scope`, `get`, `get_memory`, `list`, `list_memories`, `search_memories`, `update`, `update_memory`

#### BetaModelsOperations (8)
`create_async`, `delete`, `get`, `get_credentials`, `list`, `list_versions`, `pending_upload`, `update`

#### BetaRedTeamsOperations (3)
`create`, `get`, `list`

#### BetaRoutinesOperations (8)
`create_or_update`, `delete`, `disable`, `dispatch_async`, `enable`, `get`, `list`, `list_runs`

#### BetaSchedulesOperations (6)
`create_or_update`, `delete`, `get`, `get_run`, `list`, `list_runs`

#### BetaSkillsOperations (7)
`create`, `create_from_package`, `delete`, `download`, `get`, `list`, `update`

#### BetaToolboxesOperations (8)
`create_version`, `delete`, `delete_version`, `get`, `get_version`, `list`, `list_versions`, `update`

# AIProjectClient Subclients

This document lists all subclients available on `AIProjectClient` and their public method counts.

## Top-level Subclients

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

## Nested Subclients on `.beta`

| Subclient | Class Name | Public Methods |
|-----------|------------|----------------|
| `beta.agents` | BetaAgentsOperations | 14 |
| `beta.evaluation_taxonomies` | BetaEvaluationTaxonomiesOperations | 5 |
| `beta.evaluators` | BetaEvaluatorsOperations | 11 |
| `beta.insights` | BetaInsightsOperations | 3 |
| `beta.memory_stores` | BetaMemoryStoresOperations | 8 |
| `beta.red_teams` | BetaRedTeamsOperations | 3 |
| `beta.schedules` | BetaSchedulesOperations | 6 |
| `beta.toolboxes` | BetaToolboxesOperations | 8 |
| `beta.skills` | BetaSkillsOperations | 7 |
| `beta.datasets` | BetaDatasetsOperations | 5 |

## Summary

**Total: 102 unique public methods across all subclients**

---

### Method Details

#### AgentsOperations (8)
`get`, `delete`, `list`, `create_version`, `create_version_from_manifest`, `get_version`, `delete_version`, `list_versions`

#### EvaluationRulesOperations (4)
`get`, `delete`, `create_or_update`, `list`

#### ConnectionsOperations (3)
`list`, `get`, `get_default`

#### DatasetsOperations (9)
`list_versions`, `list`, `get`, `delete`, `create_or_update`, `pending_upload`, `get_credentials`, `upload_file`, `upload_folder`

#### DeploymentsOperations (2)
`get`, `list`

#### IndexesOperations (5)
`list_versions`, `list`, `get`, `delete`, `create_or_update`

#### TelemetryOperations (1)
`get_application_insights_connection_string`

#### BetaAgentsOperations (14)
`create_agent_version_from_code`, `create_session`, `delete_session`, `delete_session_file`, `download_agent_code`, `download_agent_version_code`, `download_session_file`, `get_session`, `get_session_files`, `get_session_log_stream`, `list_sessions`, `patch_agent_details`, `update_agent_from_code`, `upload_session_file`

#### BetaEvaluationTaxonomiesOperations (5)
`get`, `list`, `delete`, `create`, `update`

#### BetaEvaluatorsOperations (11)
`list_versions`, `list`, `get_version`, `delete_version`, `create_version`, `update_version`, `create_generation_job`, `get_generation_job`, `list_generation_jobs`, `cancel_generation_job`, `delete_generation_job`

#### BetaInsightsOperations (3)
`generate`, `get`, `list`

#### BetaMemoryStoresOperations (8)
`create`, `update`, `get`, `list`, `delete`, `delete_scope`, `search_memories`, `begin_update_memories`

#### BetaRedTeamsOperations (3)
`get`, `list`, `create`

#### BetaSchedulesOperations (6)
`delete`, `get`, `list`, `create_or_update`, `get_run`, `list_runs`

#### BetaToolboxesOperations (8)
`create_version`, `get`, `list`, `list_versions`, `get_version`, `update`, `delete`, `delete_version`

#### BetaSkillsOperations (7)
`create`, `create_from_package`, `get`, `download`, `list`, `update`, `delete`

#### BetaDatasetsOperations (5)
`get_generation_job`, `list_generation_jobs`, `create_generation_job`, `cancel_generation_job`, `delete_generation_job`

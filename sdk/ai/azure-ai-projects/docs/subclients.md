# AIProjectClient Subclients

This document lists all sub-clients available on `AIProjectClient` and their public method counts. Overload methods are not counted. Only synchronous methods are counted (but each one has an equivalent asynchronous method).

## Summary

There are a total of 132 unique public methods across all sub-clients.

### Top-level Sub-clients (stable operations)

| Subclient | Class Name | Methods Count |
|-----------|------------|----------------|
| `agents` | AgentsOperations | 8 |
| `evaluation_rules` | EvaluationRulesOperations | 4 |
| `connections` | ConnectionsOperations | 3 |
| `datasets` | DatasetsOperations | 9 |
| `deployments` | DeploymentsOperations | 2 |
| `indexes` | IndexesOperations | 5 |
| `telemetry` | TelemetryOperations | 1 |

### Nested Sub-clients (beta operations)

| Subclient | Class Name | Methods Count |
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


## Method list table

Alphabetically sorted, with ".beta" sub-client at the end.

```
.agents.create_version
.agents.create_version_from_manifest
.agents.delete
.agents.delete_version
.agents.get
.agents.get_version
.agents.list
.agents.list_versions

.connections.get
.connections.get_default
.connections.list

.datasets.create_or_update
.datasets.delete
.datasets.get
.datasets.get_credentials
.datasets.list
.datasets.list_versions
.datasets.pending_upload
.datasets.upload_file
.datasets.upload_folder

.deployments.get
.deployments.list

.evaluation_rules.create_or_update
.evaluation_rules.delete
.evaluation_rules.get
.evaluation_rules.list

.indexes.create_or_update
.indexes.delete
.indexes.get
.indexes.list
.indexes.list_versions

.telemetry.get_application_insights_connection_string

.beta.agents.cancel_optimization_job
.beta.agents.create_optimization_job
.beta.agents.create_session
.beta.agents.create_version_from_code
.beta.agents.delete_optimization_job
.beta.agents.delete_session
.beta.agents.delete_session_file
.beta.agents.download_agent_code
.beta.agents.download_session_file
.beta.agents.get_optimization_candidate
.beta.agents.get_optimization_candidate_config
.beta.agents.get_optimization_candidate_results
.beta.agents.get_optimization_job
.beta.agents.get_session
.beta.agents.get_session_files
.beta.agents.get_session_log_stream
.beta.agents.list_optimization_candidates
.beta.agents.list_optimization_jobs
.beta.agents.list_sessions
.beta.agents.patch_agent_details
.beta.agents.upload_session_file

.beta.datasets.cancel_generation_job
.beta.datasets.create_generation_job
.beta.datasets.delete_generation_job
.beta.datasets.get_generation_job
.beta.datasets.list_generation_jobs

.beta.evaluation_taxonomies.create
.beta.evaluation_taxonomies.delete
.beta.evaluation_taxonomies.get
.beta.evaluation_taxonomies.list
.beta.evaluation_taxonomies.update

.beta.evaluators.cancel_generation_job
.beta.evaluators.create_generation_job
.beta.evaluators.create_version
.beta.evaluators.delete_generation_job
.beta.evaluators.delete_version
.beta.evaluators.get_credentials
.beta.evaluators.get_generation_job
.beta.evaluators.get_version
.beta.evaluators.list
.beta.evaluators.list_generation_jobs
.beta.evaluators.list_versions
.beta.evaluators.pending_upload
.beta.evaluators.update_version

.beta.insights.generate
.beta.insights.get
.beta.insights.list

.beta.memory_stores.begin_update_memories
.beta.memory_stores.create
.beta.memory_stores.create_memory
.beta.memory_stores.delete
.beta.memory_stores.delete_memory
.beta.memory_stores.delete_scope
.beta.memory_stores.get
.beta.memory_stores.get_memory
.beta.memory_stores.list
.beta.memory_stores.list_memories
.beta.memory_stores.search_memories
.beta.memory_stores.update
.beta.memory_stores.update_memory

.beta.models.create_async
.beta.models.delete
.beta.models.get
.beta.models.get_credentials
.beta.models.list
.beta.models.list_versions
.beta.models.pending_upload
.beta.models.update

.beta.red_teams.create
.beta.red_teams.get
.beta.red_teams.list

.beta.routines.create_or_update
.beta.routines.delete
.beta.routines.disable
.beta.routines.dispatch_async
.beta.routines.enable
.beta.routines.get
.beta.routines.list
.beta.routines.list_runs

.beta.schedules.create_or_update
.beta.schedules.delete
.beta.schedules.get
.beta.schedules.get_run
.beta.schedules.list
.beta.schedules.list_runs

.beta.skills.create
.beta.skills.create_from_package
.beta.skills.delete
.beta.skills.download
.beta.skills.get
.beta.skills.list
.beta.skills.update

.beta.toolboxes.create_version
.beta.toolboxes.delete
.beta.toolboxes.delete_version
.beta.toolboxes.get
.beta.toolboxes.get_version
.beta.toolboxes.list
.beta.toolboxes.list_versions
.beta.toolboxes.update
```

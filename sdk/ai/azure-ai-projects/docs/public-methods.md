# Public AIProjectClient methods

This document lists all public methods available on `AIProjectClient` and its sub-clients. Overload methods are not counted. Only synchronous methods are counted (but each one has an equivalent asynchronous method).

## Summary

There are a total of 141 unique public methods:
- 5 stable methods on the client
- 55 stable methods on top-level sub-clients
- 81 beta methods on nested beta sub-clients

### Top-level sub-clients (stable operations)

| Subclient | Class Name | Methods Count |
|-----------|------------|----------------|
| `agents` | AgentsOperations | 23 |
| `connections` | ConnectionsOperations | 3 |
| `datasets` | DatasetsOperations | 9 |
| `deployments` | DeploymentsOperations | 2 |
| `evaluation_rules` | EvaluationRulesOperations | 4 |
| `indexes` | IndexesOperations | 5 |
| `telemetry` | TelemetryOperations | 1 |
| `toolboxes` | ToolboxesOperations | 8 |

### Nested sub-clients (beta operations)

| Subclient | Class Name | Methods Count |
|-----------|------------|----------------|
| `beta.agents` | BetaAgentsOperations | 5 |
| `beta.datasets` | BetaDatasetsOperations | 5 |
| `beta.evaluation_taxonomies` | BetaEvaluationTaxonomiesOperations | 5 |
| `beta.evaluators` | BetaEvaluatorsOperations | 13 |
| `beta.insights` | BetaInsightsOperations | 3 |
| `beta.memory_stores` | BetaMemoryStoresOperations | 13 |
| `beta.models` | BetaModelsOperations | 9 |
| `beta.red_teams` | BetaRedTeamsOperations | 3 |
| `beta.routines` | BetaRoutinesOperations | 8 |
| `beta.schedules` | BetaSchedulesOperations | 6 |
| `beta.skills` | BetaSkillsOperations | 11 |


## Stable methods on the client

Alphabetically sorted. An asterisk at the end of the method name means is a hand-written method.

```
.__enter__
.__exit__
.close
.get_openai_client*
.send_request
```

## Stable methods on top-level sub clients

Alphabetically sorted. An asterisk at the end of the method name means is a hand-written method.

```
.agents.create_session
.agents.create_version*
.agents.create_version_from_code*
.agents.create_version_from_manifest
.agents.delete
.agents.delete_session
.agents.delete_session_file
.agents.delete_version
.agents.disable
.agents.download_code
.agents.download_session_file
.agents.enable
.agents.get
.agents.get_session
.agents.get_session_log_stream
.agents.get_version
.agents.list
.agents.list_session_files
.agents.list_sessions
.agents.list_versions
.agents.stop_session
.agents.update_details
.agents.upload_session_file

.connections.get*
.connections.get_default*
.connections.list

.datasets.create_or_update
.datasets.delete
.datasets.get
.datasets.get_credentials
.datasets.list
.datasets.list_versions
.datasets.pending_upload
.datasets.upload_file*
.datasets.upload_folder*

.deployments.get
.deployments.list

.evaluation_rules.create_or_update*
.evaluation_rules.delete
.evaluation_rules.get
.evaluation_rules.list

.indexes.create_or_update
.indexes.delete
.indexes.get
.indexes.list
.indexes.list_versions

.telemetry.get_application_insights_connection_string*

.toolboxes.create_version
.toolboxes.delete
.toolboxes.delete_version
.toolboxes.get
.toolboxes.get_version
.toolboxes.list
.toolboxes.list_versions
.toolboxes.update
```

## Beta methods on nested sub-clients

Alphabetically sorted. An asterisk at the end of the method name means is a hand-written method.

```
.beta.agents.cancel_optimization_job
.beta.agents.create_optimization_job
.beta.agents.delete_optimization_job
.beta.agents.get_optimization_job
.beta.agents.list_optimization_jobs

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

.beta.memory_stores.begin_update_memories*
.beta.memory_stores.create
.beta.memory_stores.create_memory
.beta.memory_stores.delete
.beta.memory_stores.delete_memory
.beta.memory_stores.delete_scope
.beta.memory_stores.get
.beta.memory_stores.get_memory
.beta.memory_stores.list
.beta.memory_stores.list_memories
.beta.memory_stores.search_memories*
.beta.memory_stores.update
.beta.memory_stores.update_memory

.beta.models.create*
.beta.models.delete
.beta.models.get
.beta.models.get_credentials
.beta.models.list
.beta.models.list_versions
.beta.models.pending_create_version
.beta.models.pending_upload
.beta.models.update

.beta.red_teams.create
.beta.red_teams.get
.beta.red_teams.list

.beta.routines.create_or_update
.beta.routines.delete
.beta.routines.disable
.beta.routines.dispatch
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
.beta.skills.create_from_files
.beta.skills.delete
.beta.skills.delete_version
.beta.skills.download
.beta.skills.download_version
.beta.skills.get
.beta.skills.get_version
.beta.skills.list
.beta.skills.list_versions
.beta.skills.update
```

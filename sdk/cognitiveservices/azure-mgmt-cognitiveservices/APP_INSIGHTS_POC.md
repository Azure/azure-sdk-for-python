# Foundry Project Application Insights POC

This prototype evaluates whether the Python management SDK can temporarily
compose the ARM calls needed to create a Foundry project with default
Application Insights while the service-owned AccountRP/GSO implementation is
being built.

It is an exploratory bridge, not a proposed permanent ownership model.

## Preview API

```python
project = client.projects.create_with_default_app_insights(
    resource_group_name="my-resource-group",
    account_name="my-foundry-account",
    project_name="my-project",
    project={
        "identity": {"type": "SystemAssigned"},
        "location": "eastus2",
        "properties": {"displayName": "my-project"},
    },
    app_insights_auth="api_key",
)
```

`api_key` is the default because it matches the current automatic
create-project UI flow. `project_managed_identity` disables local
authentication on Application Insights, assigns Monitoring Metrics Publisher
to the project identity, and creates a Project Managed Identity connection.

## Live Feasibility Results

Live validation began on October 14, 2026 in a corporate test subscription.
The stages are recorded independently so one blocked service route does not
hide the feasibility of later ARM operations.

| Stage | Result | Finding |
|---|---|---|
| Create `AIServices` account | Working | System-assigned identity, custom subdomain, and `allowProjectManagement=true` provisioned successfully in `eastus2`. |
| Create project in East US 2 | Blocked by regional dependency | Both `2026-09-15-preview` and `2025-06-01` returned service-side `InternalServerError`. AccountRP traces showed its hidden ARM deployment attempted an Azure AI Search `serverless` service, which is not offered in East US 2. |
| Create project in Central US | Blocked by hidden deployment conflict | Search serverless is offered, but the hidden CommonHobo Search deployment reached a terminal `Failed` state with a generic ARM `Conflict`. |
| Create project in West US 2 | Working | The project and backend workspace reached `Succeeded`. The generated LRO completed before backend readiness, so the POC explicitly polls project state before creating connections. |
| Create Log Analytics workspace | Working | The SDK created the deterministic account-scoped workspace with `PerGB2018` and 30-day retention. |
| Create workspace-based Application Insights | Working | The SDK created the component and linked it to the new Log Analytics workspace. |
| Create project API Key connection | Working | West US 2 produced an `AppInsights`/`ApiKey` project connection while keeping the connection string internal to the SDK. |
| Create project PMI connection | Working | West US 2 produced an `AppInsights`/`ProjectManagedIdentity` connection, disabled local auth, and created one Monitoring Metrics Publisher assignment. |
| Retry both modes | Working | Re-running both complete calls reused the same project, workspace, component, connection, and deterministic role assignment. |
| API Key secret handling | Working locally | The connection string remains internal to the orchestration and is omitted from returned values and stage-specific exceptions. |
| PMI role assignment and connection | Working live | Payload, deterministic role ID, local-auth setting, propagation retry, and required connection metadata are covered by tests and live validation. |

Observed project-create request identifiers:

- `729e59a7-124d-48c9-ab47-2cbf6ff2fd22`
- `df48fb03-2393-48b6-97bf-e108745e4d0d`
- Stable API request ID: `037c6879-9db6-46e2-be27-1451dbaec4de`

These identifiers contain no credentials and can be used by the service team to
trace why project backend provisioning failed.

Working live resources used the `sdk-appinsights-poc-account-wus2` account in
West US 2 with separate `sdk-appinsights-apikey-poc` and
`sdk-appinsights-pmi-poc` projects. No credentials or connection strings are
recorded in this document.

## What the POC Proves

- A handwritten Python SDK customization can reuse the caller's credential to
  orchestrate Cognitive Services, Log Analytics, Application Insights, and
  Authorization clients.
- Default Log Analytics and workspace-based Application Insights provisioning
  works with ordinary provider defaults; no special quota or configuration
  increases were required.
- The orchestration can be idempotent through ARM create-or-update calls,
  deterministic names, a stable connection name, and a deterministic role
  assignment UUID.
- API Key mode can match the current UI implementation without asking the
  customer to provide, receive, or manage a connection string.
- Project Managed Identity can be represented with the required Azure Monitor
  audience and AccountRP metadata even though the generated model currently has
  no dedicated PMI connection subclass.

## Pitfalls and Unknowns

- Project creation is the critical dependency. A successful ARM account is not
  enough; the backend workspace registration must also succeed before project
  connections can be created.
- Region selection must account for hidden project dependencies. The tested
  project flow implicitly creates Azure AI Search `serverless`; selecting a
  region without that SKU causes the project to fail even though the Foundry
  account itself succeeds.
- The generated project LRO is not a sufficient readiness signal for project
  connections. The project resource must be polled until its provisioning state
  is `Succeeded`.
- Cross-provider orchestration is not atomic. A failed project connection can
  leave a project, workspace, component, or role assignment that a retry must
  reconcile.
- The caller needs permissions across four providers, including role assignment
  write permission for PMI mode.
- API Key and PMI modes require separate Application Insights resources during
  comparison because `DisableLocalAuth` is resource-scoped.
- Shared account-level resources create concurrency and deletion questions that
  the Python SDK should not own permanently.
- The generated connection schema recognizes the
  `ProjectManagedIdentity` discriminator but does not expose its `audience`
  field as a dedicated model. The POC sends the connection as a raw dictionary,
  which the generated operation serializes directly.
- Public ARM project failures are too generic to diagnose without service-side
  traces. East US 2 surfaced only `InternalServerError` publicly, while the
  AccountRP trace identified the unsupported hidden Search SKU.
- A region advertising Search serverless support can still encounter an
  internal CommonHobo deployment conflict, as observed in Central US.

## Permanent Direction

The permanent implementation should live in AccountRP/GSO so every client gets
the same behavior, the service can own retries and lifecycle, and customer
credentials do not need cross-provider permissions. Once that exists, this
preview method can delegate to ordinary project creation and the auxiliary
management dependencies can be removed.

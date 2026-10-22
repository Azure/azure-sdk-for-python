using './sample-resources.bicep'

// Non-deployable placeholders keep editor validation offline. The orchestrator requires every live binding.
param accountName = readEnvironmentVariable('SAMPLE_CI_ACCOUNT_NAME', 'unconfigured-account')
param projectName = readEnvironmentVariable('SAMPLE_CI_PROJECT_NAME', 'unconfigured-project')
param runnerPrincipalId = readEnvironmentVariable('SAMPLE_CI_RUNNER_PRINCIPAL_ID', '00000000-0000-0000-0000-000000000000')
param agentName = readEnvironmentVariable('SAMPLE_CI_AGENT_NAME', 'unconfigured-agent')
param sampleModel = {
  name: readEnvironmentVariable('SAMPLE_CI_MODEL_NAME', 'unconfigured-model')
  version: readEnvironmentVariable('SAMPLE_CI_MODEL_VERSION', 'unconfigured-version')
  sku: readEnvironmentVariable('SAMPLE_CI_MODEL_SKU', 'GlobalStandard')
  capacity: int(readEnvironmentVariable('SAMPLE_CI_MODEL_CAPACITY', '1'))
}
param validationModel = {
  name: 'gpt-5.2'
  version: readEnvironmentVariable('SAMPLE_CI_VALIDATION_MODEL_VERSION', 'unconfigured-version')
  sku: 'GlobalStandard'
  capacity: int(readEnvironmentVariable('SAMPLE_CI_VALIDATION_MODEL_CAPACITY', '1'))
}
param provisionMcp = bool(readEnvironmentVariable('SAMPLE_CI_PROVISION_MCP', 'false'))
param mcpPat = readEnvironmentVariable('MCP_GITHUB_PAT', '')

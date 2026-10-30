using './sample-resources.bicep'

// Non-deployable placeholders keep editor validation offline. The orchestrator requires every live binding.
param accountName = readEnvironmentVariable('SAMPLE_CI_ACCOUNT_NAME', 'unconfigured-account')
param projectName = readEnvironmentVariable('SAMPLE_CI_PROJECT_NAME', 'unconfigured-project')
param agentName = readEnvironmentVariable('SAMPLE_CI_AGENT_NAME', 'unconfigured-agent')
param sampleModel = {
  name: readEnvironmentVariable('SAMPLE_CI_MODEL_NAME', 'unconfigured-model')
  version: readEnvironmentVariable('SAMPLE_CI_MODEL_VERSION', 'unconfigured-version')
  sku: readEnvironmentVariable('SAMPLE_CI_MODEL_SKU', 'GlobalStandard')
  capacity: int(readEnvironmentVariable('SAMPLE_CI_MODEL_CAPACITY', '1'))
}
param mcpPat = readEnvironmentVariable('MCP_GITHUB_PAT', '')

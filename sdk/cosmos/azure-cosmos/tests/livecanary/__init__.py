# Live multi-region canary tests for hedging detection (AC13).
#
# These tests are skipped by default. To run, set:
#   COSMOS_MULTI_REGION_ENDPOINT
#   COSMOS_MULTI_REGION_KEY
#   COSMOS_MULTI_REGION_DATABASE
#   COSMOS_MULTI_REGION_CONTAINER
# against a multi-region Cosmos DB account with at least two preferred regions
# in distinct geographies (otherwise the threshold-based hedge arms never
# dispatch and the test cannot observe HEDGING entries).

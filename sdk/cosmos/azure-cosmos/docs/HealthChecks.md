# Overview
The getDatabaseAccount call is a crucial metadata request the SDK makes to the Cosmos DB gateway. It currently serves two primary purposes:
 - Topology Discovery: To retrieve the service configuration of your database account, including the authoritative list of readable and writable regions.
 - Health Check: To proactively check the health of regional endpoints by making this call against the global endpoint and preferred regional endpoints. A failure marks the corresponding region as unavailable.
This behavior is evolving, and future updates plan to separate the health check mechanism from this call. 

---
## Mock Data Flow Example
Account Configuration:
    Account Name: my-test-account
    Primary Write Region: West US
    Secondary Read Region: East US
    Global Endpoint: https://my-test-account.documents.azure.com:443/

### Step 1: Client Initialization
You create a CosmosClient instance, pointing it to your account's global endpoint.
```python
client = CosmosClient(
    url="https://my-test-account.documents.azure.com:443/",
    credential=my_credential
)
```

### Step 2: The Initial getDatabaseAccount Call
Upon initialization, the SDK makes a GET request to the global endpoint to discover the account's topology.
Request: GET https://my-test-account.documents.azure.com:443/
The Cosmos DB gateway responds with a JSON object (the DatabaseAccount resource) containing your account's configuration.
(mock data)
```python
{
  "writableLocations": [
    {
      "name": "West US",
      "databaseAccountEndpoint": "https://my-test-account-westus.documents.azure.com:443/"
    }
  ],
  "readableLocations": [
    {
      "name": "West US",
      "databaseAccountEndpoint": "https://my-test-account-westus.documents.azure.com:443/"
    },
    {
      "name": "East US",
      "databaseAccountEndpoint": "https://my-test-account-eastus.documents.azure.com:443/"
    }
  ],
  "enableMultipleWriteLocations": False,
  // ... other properties
}
```

### Step 3: Populating the Location Cache
The SDK's internal LocationCache parses this JSON to build a "map" of your account's regions.
 Write Endpoints: ["https://my-test-account-westus.documents.azure.com:443/"]
 Read Endpoints: ["https://my-test-account-westus.documents.azure.com:443/", "https://my-test-account-eastus.documents.azure.com:443/"]

### Step 4: Routing a Data Request
When your application performs an operation (e.g., read_item), the LocationCache uses this map to route the request to the most appropriate regional endpoint, 
respecting user preferences and endpoint health.

---
## Periodic Refresh and Health Check Behavior
After initialization, the SDK periodically refreshes this information.
### Frequency and Targets
By default, the SDK calls getDatabaseAccount every `5 minutes` to get the latest topology and check endpoint health. These calls are made to both the 
global endpoint (e.g., https://my-account.documents.azure.com) and the specific endpoint for each user-preferred region.
Why Check the Global Endpoint?: While the global endpoint resolves to one of the regional endpoints (typically the primary write region), checking it is critical. 
It verifies the health of the primary DNS entry and the global gateway, which is the authoritative source for the account's topology. 
A failure to connect to the global endpoint can signal a different problem (like a DNS issue or a global service impairment) than a regional outage. 
### Retry on Failure
The getDatabaseAccount call has a built-in retry policy for transient failures.
Transient Errors: These include `timeouts, connection errors, and certain HTTP status codes (e.g., 5xx ServiceUnavailable, 408 RequestTimeout)`.
Retry Logic: By default, the SDK will retry the call up to `3 times` with a `100ms` delay between attempts. If all retries against a specific endpoint (global or regional) fail, the SDK marks that regional endpoint as unavailable in the LocationCache.
Configuration: The number of retries and the delay are configurable via environment variables.
Example: If a client has two preferred regions, the SDK will issue 3 getDatabaseAccount calls every 5 minutes (1 for the global endpoint + 2 for the preferred regions). If those regions are experiencing transient issues, the retry logic could result in up to 9 total attempts (3 endpoints × 3 retries) within that 5-minute window.
### Dedicated Health Probes
The current dual responsibility of the getDatabaseAccount call is being refactored. A future update will introduce a dedicated health check probe.
After the Change: The getDatabaseAccount call will no longer be used to determine endpoint health or to mark regions as unavailable.
New Role: Its sole purpose will be to fetch the account topology (the writableLocations and readableLocations) and updating the location cache. A new, separate health probe will be responsible for actively monitoring endpoint availability.
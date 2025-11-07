# simple_agent_with_redis_checkpointer

This sample demonstrates a LangGraph-based simple agent that uses an Azure managed Redis instance as a checkpointer. 

# Prerequisites
Create an Azure Managed Redis instance

1) Install the Redis Enterprise CLI extension (if not already installed)
    ```
    az extension add --name redisenterprise
    ```

2) Create a resource group (example)
    ```
    az group create --name myRedisRG --location eastus
    ```

3) Create a Redis Enterprise instance with RedisJSON and RediSearch modules enabled
   Create an [Azure Managed Redis instance](https://learn.microsoft.com/azure/redis/quickstart-create-managed-redis). For LangGraph checkpointer, the instance must have RedisJSON and RediSearch enabled. Clustering-policy should be EnterpriseCluster. Those configurations have to be set when creating. Redis sku and capacities can be configured with your needs.

   When your redis instance is ready, add the redis information to environment variables.

# Setup

1. **Environment Configuration**
   Create a `.env` file in this directory with your Azure OpenAI and Redis configuration:
   ```
    AZURE_OPENAI_API_KEY=<api-key>
    AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
    OPENAI_API_VERSION=2025-03-01-preview
    CHECKPOINTER_REDIS_URL=<name>.<region>.redis.azure.net
    CHECKPOINTER_REDIS_KEY=<redis-key>
    CHECKPOINTER_REDIS_PORT=10000
   ```
   And install python-dotenv
   ```bash
   pip install python-dotenv langgraph-checkpoint-redis
   ```

2. **Install Dependencies**
   Required Python packages (install via pip):
   ```bash
   cd  container_agents/container_agent_adapter/python
   pip install -e .[langgraph]
   ```


# Running as HTTP Server

1. Start the agent server:
   ```bash
   python main.py
   ```
   The server will start on `http://localhost:8088`

2. Test the agent:
   ```bash
   curl -X POST http://localhost:8088/responses \
     -H "Content-Type: application/json" \
     -d '{
       "agent": {
         "name": "local_agent",
         "type": "agent_reference"
       },
       "stream": false,
       "input": "What is 15 divided by 3?",
       "conversation": {"id": "test-conversation-id"}
     }'
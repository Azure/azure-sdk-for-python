# 获取 token
TOKEN=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv)

echo "Token obtained, sending streaming request..."
echo "================================"
echo ""

curl -N -v --no-buffer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -X POST https://ai-account-x3pxnw7bdbexq.services.ai.azure.com/api/projects/ai-project-test-hugging-face-agent/agents/HuggingFace-Agent/versions/2/responses \
  -d "{\"input\":[{\"role\":\"user\",\"content\":\"What are the trending models in the OpenLLM Leaderboard?\"}],\"stream\":true}"
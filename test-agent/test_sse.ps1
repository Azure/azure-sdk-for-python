# PowerShell 版本 - 查看原始 SSE 流

# 获取 token
Write-Host "Getting Azure token..."
$TOKEN = az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv

if (-not $TOKEN) {
    Write-Host "Failed to get token. Please run 'az login' first."
    exit 1
}

Write-Host "Token obtained, sending streaming request..."
Write-Host "================================"
Write-Host ""

# 发送请求，显示原始 SSE 流
curl.exe -N -v --no-buffer `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $TOKEN" `
  -X POST "https://ai-account-x3pxnw7bdbexq.services.ai.azure.com/api/projects/ai-project-test-hugging-face-agent/agents/HuggingFace-Agent/versions/2/responses?api-version=2024-10-01-preview" `
  -d "{`"input`":[{`"role`":`"user`",`"content`":`"What are the trending models in the OpenLLM Leaderboard?`"}],`"stream`":true}"

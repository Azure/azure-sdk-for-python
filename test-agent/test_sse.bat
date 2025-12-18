echo Getting Azure token...
for /f "delims=" %%i in ('az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv') do set TOKEN=%%i

if "%TOKEN%"=="" (
    echo Failed to get token. Please run 'az login' first.
    exit /b 1
)

echo Token obtained, sending streaming request...
echo ================================
echo.


curl -N -v --no-buffer ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -X POST "https://ai-account-x3pxnw7bdbexq.services.ai.azure.com/api/projects/ai-project-test-hugging-face-agent/agents/HuggingFace-Agent/versions/2/responses?api-version=2025-03-01-preview" ^
  -d "{\"input\":[{\"role\":\"user\",\"content\":\"What are the trending models in the OpenLLM Leaderboard?\"}],\"stream\":true}"

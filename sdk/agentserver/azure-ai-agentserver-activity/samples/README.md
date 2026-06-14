# Activity Protocol Samples

Samples for the `azure-ai-agentserver-activity` package, demonstrating the Activity protocol
for Foundry hosted agents. Each sample is based on a corresponding sample from the
[Microsoft 365 Agents SDK](https://github.com/microsoft/Agents/tree/main/samples/python).

## Samples

| Sample | Based on | What it demonstrates | Pattern |
| --- | --- | --- | --- |
| [`simple_activity_agent`](#simple_activity_agent) | [quickstart](https://github.com/microsoft/Agents/tree/main/samples/python/quickstart) | Echo bot with welcome, invoke, installationUpdate, error handling | Zero-config decorator |
| [`streaming_activity_agent`](#streaming_activity_agent) | [azureai-streaming](https://github.com/microsoft/Agents/tree/main/samples/python/azureai-streaming) | Azure OpenAI streaming via `context.streaming_response` | Zero-config decorator |
| [`cards_activity_agent`](#cards_activity_agent) | [cards](https://github.com/microsoft/Agents/tree/main/samples/python/cards) | Adaptive Cards, Hero Cards, Thumbnail Cards, Receipt Cards | Zero-config decorator |
| [`auto_signin_activity_agent`](#auto_signin_activity_agent) | [auto-signin](https://github.com/microsoft/Agents/tree/main/samples/python/auto-signin) | OAuth auto sign-in with Graph and GitHub providers | Handler (for `auth_handlers`) |
| [`semantic_kernel_activity_agent`](#semantic_kernel_activity_agent) | [semantic-kernel-multiturn](https://github.com/microsoft/Agents/tree/main/samples/python/semantic-kernel-multiturn) | Semantic Kernel agent with tools, multi-turn, streaming | Zero-config decorator |
| [`suggested_actions_activity_agent`](#suggested_actions_activity_agent) | [suggested-actions](https://github.com/microsoft/BotBuilder-Samples/tree/main/samples/python/08.suggested-actions) | Quick-reply buttons that disappear after tap | Zero-config decorator |

### Usage patterns

- **Zero-config decorator** — The simplest pattern. `ActivityAgentServerHost` auto-initializes the
  M365 Agents SDK from environment variables. You write only handler logic:
  ```python
  app = ActivityAgentServerHost()

  @app.activity("message")
  async def on_message(context, state):
      await context.send_activity(f"Echo: {context.activity.text}")

  app.run()
  ```

- **Handler** — Full control. You create the M365 SDK `AgentApplication` yourself and pass a custom
  handler. Required for M365-specific features like `auth_handlers` or regex-matched `@AGENT_APP.message()`:
  ```python
  AGENT_APP = AgentApplication[TurnState](storage=..., adapter=..., ...)

  @AGENT_APP.message("/me", auth_handlers=["GRAPH"])
  async def on_me(context, state): ...

  async def handle(request):
      activity = Activity.model_validate(request.state.activity)
      await ADAPTER.process_activity(claims, activity, AGENT_APP.on_turn)
      return Response(status_code=202)

  app = ActivityAgentServerHost(handler=handle)
  ```

## simple_activity_agent

The simplest activity protocol agent. Echoes messages back, welcomes new members,
handles installation events, and processes invoke activities. Zero SDK wiring needed.

- `@app.activity("conversationUpdate")` — welcome new members
- `@app.activity("message")` — echo user text
- `@app.activity("invoke")` — handle adaptive card actions / task modules
- `@app.activity("installationUpdate")` — add/remove events
- `@app.error` — error handler

## streaming_activity_agent

Streams Azure OpenAI completions token-by-token to the user in Teams using
the M365 SDK's `context.streaming_response`:

- `context.streaming_response.set_generated_by_ai_label(True)` — AI content label
- `context.streaming_response.set_feedback_loop(True)` — enable thumbs up/down
- `context.streaming_response.queue_informative_update(...)` — status text
- `context.streaming_response.queue_text_chunk(...)` — streamed tokens
- `context.streaming_response.end_stream()` — completion signal

**Requires:** `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_MODEL`

## cards_activity_agent

Shows rich card types to enhance conversation design:

- **Adaptive Card** — interactive form with text input, dropdown, and submit button
- **Hero Card** — large image, title, subtitle, action buttons
- **Thumbnail Card** — compact layout with thumbnail image
- **Receipt Card** — line items, totals, and action buttons

Handles Adaptive Card submit actions via `@app.activity("invoke")`.

## auto_signin_activity_agent

OAuth auto sign-in with multiple providers. Uses the handler pattern because
`auth_handlers` is an `AgentApplication` feature.

- `@AGENT_APP.message("/me", auth_handlers=["GRAPH"])` — Graph profile
- `@AGENT_APP.message("/prs", auth_handlers=["GITHUB"])` — GitHub repos
- `@AGENT_APP.message("/status")` — token status
- `@AGENT_APP.message("/logout")` — sign out

**Requires:** OAuth connection names in environment variables (see sample docstring).

## semantic_kernel_activity_agent

Multi-turn weather agent built with Semantic Kernel. Demonstrates function calling
with custom plugins and streaming responses.

- `DateTimePlugin` — provides current date/time
- `WeatherPlugin` — simulated weather data (replace with real API)
- `ChatCompletionAgent` with `FunctionChoiceBehavior.Auto()`
- Multi-turn conversation with in-memory session history
- Streaming via `context.streaming_response`

**Requires:** `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_MODEL`

## suggested_actions_activity_agent

Quick-reply buttons that disappear after the user taps one. Based on
the BotBuilder `08.suggested-actions` sample.

- `SuggestedActions` with `CardAction(type="imBack", ...)` buttons
- Buttons disappear after selection (unlike card buttons which persist)
- Re-prompts with new suggestions after each response
- Great for guided menus, confirmations, and quick choices

## Running

```bash
# Set M365 SDK env vars (auto-injected in Foundry hosted containers)
export CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=<app-id>
export CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE=UserManagedIdentity
export CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY=https://login.microsoftonline.com/<tenant-id>
export CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=<tenant-id>

# Install dependencies
pip install -r <sample_folder>/requirements.txt

# Run
python <sample_folder>/<sample_file>.py
```

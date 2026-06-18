"""
DESCRIPTION:
    Function tools that connect the orchestrator agent to its three
    sub-agents (onboarding, researcher, triage). Each `ask_*` function
    forwards a question to the corresponding sub-agent via the Responses
    API, threads the per-subagent `previous_response_id` so the sub-agent
    sees its own history, and returns the sub-agent's `answer` so the
    orchestrator can show it verbatim. 

    - `trace(response)`: prints all output item (reasoning, text, tool
      calls, MCP calls, web calls) on one line each, for debugging.
    - `dispatch_tools(response)`: executes any `function_call` items in a
      response, packages their results as `FunctionCallOutput` entries to
      feed back, and returns the first sub-agent `answer`.

"""

import json
from typing import Any, Callable
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam
from azure.ai.projects.models import FunctionTool


onboarding_global: dict[str, Any] = {"client": None, "agent_name": None, "previous_response_id": None}
researcher_global: dict[str, Any] = {"client": None, "agent_name": None, "previous_response_id": None}
triage_global: dict[str, Any] = {"client": None, "agent_name": None, "previous_response_id": None}


def bind_onboarding(openai_client: Any, agent_name: str) -> None:
    """Bind the OpenAI client and onboarding agent name used by ``ask_onboarding``."""
    onboarding_global["client"] = openai_client
    onboarding_global["agent_name"] = agent_name
    onboarding_global["previous_response_id"] = None


def bind_researcher(openai_client: Any, agent_name: str) -> None:
    """Bind the OpenAI client and researcher agent name used by ``ask_researcher``."""
    researcher_global["client"] = openai_client
    researcher_global["agent_name"] = agent_name
    researcher_global["previous_response_id"] = None


def bind_triage(openai_client: Any, agent_name: str) -> None:
    """Bind the OpenAI client and triage agent name used by ``ask_triage``."""
    triage_global["client"] = openai_client
    triage_global["agent_name"] = agent_name
    triage_global["previous_response_id"] = None


def ask_onboarding(question: str, context: str = "") -> dict[str, Any]:
    """Delegate a question to the onboarding sub-agent and return its answer."""
    if onboarding_global["client"] is None or onboarding_global["agent_name"] is None:
        return {"error": "onboarding agent is not bound; call bind_onboarding() first."}

    prompt = f"{context}\n\n{question}".strip() if context else question
    kwargs: dict[str, Any] = {
        "input": prompt,
        "extra_body": {"agent_reference": {"name": onboarding_global["agent_name"], "type": "agent_reference"}},
    }
    if onboarding_global["previous_response_id"]:
        kwargs["previous_response_id"] = onboarding_global["previous_response_id"]
    response = onboarding_global["client"].responses.create(**kwargs)
    onboarding_global["previous_response_id"] = response.id
    return {"answer": response.output_text}


def ask_onboarding_tool() -> FunctionTool:
    """`ask_onboarding` function tool that delegates to the onboarding sub-agent."""
    return FunctionTool(
        name="ask_onboarding",
        description=(
            "Delegate to the onboarding subagent for first-time setup help (install, "
            "az login, env vars, first-sample walkthroughs). Present the returned "
            "`answer` verbatim."
        ),
        parameters={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's question, rephrased for onboarding."},
                "context": {"type": "string", "description": "Optional extra context."},
            },
            "required": ["question", "context"],
            "additionalProperties": False,
        },
        strict=True,
    )


def ask_researcher(question: str) -> dict[str, Any]:
    """Delegate a question to the researcher sub-agent and return its answer."""
    if researcher_global["client"] is None or researcher_global["agent_name"] is None:
        return {"error": "researcher agent is not bound; call bind_researcher() first."}

    kwargs: dict[str, Any] = {
        "input": question,
        "extra_body": {"agent_reference": {"name": researcher_global["agent_name"], "type": "agent_reference"}},
    }
    if researcher_global["previous_response_id"]:
        kwargs["previous_response_id"] = researcher_global["previous_response_id"]
    response = researcher_global["client"].responses.create(**kwargs)
    trace(response)
    researcher_global["previous_response_id"] = response.id
    return {"answer": response.output_text}


def ask_researcher_tool() -> FunctionTool:
    """`ask_researcher` function tool that delegates to the researcher sub-agent."""
    return FunctionTool(
        name="ask_researcher",
        description=(
            "Delegate to the researcher subagent for any question that needs real repo "
            "content: cross-language comparisons, inconsistency checks, spec-vs-code "
        ),
        parameters={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The full question to research'",
                },
            },
            "required": ["question"],
            "additionalProperties": False,
        },
        strict=True,
    )


def ask_triage(question: str) -> dict[str, Any]:
    """Delegate a question to the triage sub-agent and return its answer."""
    if triage_global["client"] is None or triage_global["agent_name"] is None:
        return {"error": "triage agent is not bound; call bind_triage() first."}

    kwargs: dict[str, Any] = {
        "input": question,
        "extra_body": {"agent_reference": {"name": triage_global["agent_name"], "type": "agent_reference"}},
    }
    if triage_global["previous_response_id"]:
        kwargs["previous_response_id"] = triage_global["previous_response_id"]
    response = triage_global["client"].responses.create(**kwargs)
    triage_global["previous_response_id"] = response.id
    return {"answer": response.output_text}


def ask_triage_tool() -> FunctionTool:
    """`ask_triage` function tool that delegates to the triage sub-agent."""
    return FunctionTool(
        name="ask_triage",
        description=(
            "Delegate to the triage subagent for live engineering signal: open PRs, "
            "open issues, recent activity, error-message diagnosis via issue search. "
            "Triage owns the github MCP server "
            "PR/issue numbers and statuses you can show the user."
        ),
        parameters={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "What to look up on GitHub, e.g. 'List open PRs for azure-ai-projects' or 'Search issues for DefaultAzureCredential 401'.",
                },
            },
            "required": ["question"],
            "additionalProperties": False,
        },
        strict=True,
    )


functions: dict[str, Callable[..., Any]] = {
    "ask_onboarding": ask_onboarding,
    "ask_researcher": ask_researcher,
    "ask_triage": ask_triage,
}

def trace(response: Any) -> None:
    """Print every item in a response: reasoning, text, tool calls, MCP/Bing calls."""
    items = list(response.output)
    if not items:
        print("  [empty-response]")
        return
    for item in items:
        t = getattr(item, "type", "?")
        if t == "reasoning":
            text = "".join(
                getattr(s, "text", "") for s in getattr(item, "summary", []) or []
            ).strip()
            print(f"  [reasoning] {text}" if text else "  [reasoning] (empty)")
        elif t == "message":
            parts = getattr(item, "content", []) or []
            if not parts:
                print("  [message] (empty)")
                continue
            for c in parts:
                text = getattr(c, "text", "")
                if text:
                    print(f"  [text] {text}")
                else:
                    print(f"  [message] (empty content, type={getattr(c, 'type', '?')})")
        elif t == "function_call":
            print(f"  [tool] {item.name}({item.arguments})")
        elif t == "mcp_call":
            print(f"  [mcp] {getattr(item, 'name', '?')} on {getattr(item, 'server_label', '?')}")
        elif t == "mcp_list_tools":
            print(f"  [mcp_list_tools] list_tools on {getattr(item, 'server_label', '?')}")
        elif t in ("bing_grounding_call", "web_search_call"):
            q = getattr(getattr(item, "action", None), "query", "?")
            print(f"  [web] {q}")
        else:
            print(f"  [{t}]")


def dispatch_tools(response: Any) -> tuple[ResponseInputParam, str | None]:
    """Execute ``function_call`` items in ``response`` and return ``(outputs, verbatim)``.

    """
    outputs: ResponseInputParam = []
    verbatim: str | None = None
    for item in response.output:
        if item.type != "function_call" or item.name not in functions:
            continue
        call_args = json.loads(item.arguments) if item.arguments else {}
        try:
            result = functions[item.name](**call_args)
        except Exception as exc:
            result = {"error": f"{type(exc).__name__}: {exc}"}
        if (
            verbatim is None
            and item.name in {"ask_researcher", "ask_triage", "ask_onboarding"}
            and isinstance(result, dict)
            and "answer" in result
        ):
            verbatim = result["answer"]
        preview = json.dumps(result)
        if isinstance(result, dict) and "error" in result:
            print(f"  [tool-result] {preview}")
        else:
            print(f"  [tool-result] {preview[:200]}{'...' if len(preview) > 200 else ''}")
        outputs.append(
            FunctionCallOutput(
                type="function_call_output",
                call_id=item.call_id,
                output=json.dumps(result),
            )
        )
    return outputs, verbatim

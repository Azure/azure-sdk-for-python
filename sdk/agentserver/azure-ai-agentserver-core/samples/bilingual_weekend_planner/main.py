# mypy: ignore-errors
"""Bilingual weekend planner sample with full GenAI telemetry capture."""


import json
import logging
import os
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
from urllib.parse import urlparse

import azure.identity
import openai
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_default_openai_client,
    set_tracing_disabled,
)
from agents.tracing import (
    agent_span as tracing_agent_span,
    function_span as tracing_function_span,
    generation_span as tracing_generation_span,
    trace as tracing_trace,
)
from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.models import (
    CreateResponse,
    Response as OpenAIResponse,
)
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponseCompletedEvent,
    ResponseCreatedEvent,
    ResponseOutputItemAddedEvent,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from rich.logging import RichHandler

try:
    from azure.monitor.opentelemetry.exporter import (  # mypy: ignore
        AzureMonitorTraceExporter,
    )
except Exception:  # pragma: no cover
    AzureMonitorTraceExporter = None  # mypy: ignore

# Load env early so adapter init sees them
load_dotenv(override=True)


logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
logger = logging.getLogger("bilingual_weekend_planner")
RUN_MODE = os.getenv("WEEKEND_PLANNER_MODE", "container").lower()


@dataclass
class _ApiConfig:
    """Helper describing how to create the OpenAI client."""

    build_client: Callable[[], openai.AsyncOpenAI]
    model_name: str
    base_url: str
    provider: str


def _set_capture_env(provider: str, base_url: str) -> None:
    """Enable all GenAI capture toggles prior to instrumentation."""

    capture_defaults = {
        "OTEL_INSTRUMENTATION_OPENAI_AGENTS_CAPTURE_CONTENT": "true",
        "OTEL_INSTRUMENTATION_OPENAI_AGENTS_CAPTURE_METRICS": "true",
        "OTEL_GENAI_CAPTURE_MESSAGES": "true",
        "OTEL_GENAI_CAPTURE_SYSTEM_INSTRUCTIONS": "true",
        "OTEL_GENAI_CAPTURE_TOOL_DEFINITIONS": "true",
        "OTEL_GENAI_EMIT_OPERATION_DETAILS": "true",
        "OTEL_GENAI_AGENT_NAME": os.getenv(
            "OTEL_GENAI_AGENT_NAME",
            "Bilingual Weekend Planner Agent",
        ),
        "OTEL_GENAI_AGENT_DESCRIPTION": os.getenv(
            "OTEL_GENAI_AGENT_DESCRIPTION",
            "Assistant that plans weekend activities using weather and events data in multiple languages",
        ),
        "OTEL_GENAI_AGENT_ID": os.getenv(
            "OTEL_GENAI_AGENT_ID", "bilingual-weekend-planner"
        ),
    }
    for env_key, value in capture_defaults.items():
        os.environ.setdefault(env_key, value)

    parsed = urlparse(base_url)
    if parsed.hostname:
        os.environ.setdefault("OTEL_GENAI_SERVER_ADDRESS", parsed.hostname)
    if parsed.port:
        os.environ.setdefault("OTEL_GENAI_SERVER_PORT", str(parsed.port))


def _resolve_api_config() -> _ApiConfig:
    """Return the client configuration for the requested host."""

    host = os.getenv("API_HOST", "github").lower()

    if host == "github":
        base_url = os.getenv(
            "GITHUB_OPENAI_BASE_URL",
            "https://models.inference.ai.azure.com",
        ).rstrip("/")
        model_name = os.getenv("GITHUB_MODEL", "gpt-4o")
        api_key = os.environ.get("GITHUB_TOKEN")
        if not api_key:
            if RUN_MODE != "demo":
                raise RuntimeError("GITHUB_TOKEN is required when API_HOST=github")
            api_key = "demo-key"

        def _build_client() -> openai.AsyncOpenAI:
            return openai.AsyncOpenAI(base_url=base_url, api_key=api_key)

        return _ApiConfig(
            build_client=_build_client,
            model_name=model_name,
            base_url=base_url,
            provider="azure.ai.inference",
        )

    if host == "azure":
        # Explicitly check for required environment variables
        if "AZURE_OPENAI_ENDPOINT" not in os.environ:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required when API_HOST=azure")
        if "AZURE_OPENAI_VERSION" not in os.environ:
            raise ValueError("AZURE_OPENAI_VERSION is required when API_HOST=azure")
        if "AZURE_OPENAI_CHAT_DEPLOYMENT" not in os.environ:
            raise ValueError(
                "AZURE_OPENAI_CHAT_DEPLOYMENT is required when API_HOST=azure"
            )
        endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
        api_version = os.environ["AZURE_OPENAI_VERSION"]
        deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

        credential = azure.identity.DefaultAzureCredential()
        token_provider = azure.identity.get_bearer_token_provider(
            credential,
            "https://cognitiveservices.azure.com/.default",
        )

        def _build_client() -> openai.AsyncAzureOpenAI:
            return openai.AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
            )

        return _ApiConfig(
            build_client=_build_client,
            model_name=deployment,
            base_url=endpoint,
            provider="azure.ai.openai",
        )

    raise ValueError(
        f"Unsupported API_HOST '{host}'. Supported values are 'github' or 'azure'."
    )


def _configure_otel() -> None:
    """Configure the tracer provider and exporters."""

    grpc_endpoint = os.getenv("OTEL_EXPORTER_OTLP_GRPC_ENDPOINT")
    if not grpc_endpoint:
        default_otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        protocol = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc").lower()
        if default_otlp_endpoint and protocol == "grpc":
            grpc_endpoint = default_otlp_endpoint

    conn = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")
    resource = Resource.create(
        {
            "service.name": "weekend-planner-service",
            "service.namespace": "leisure-orchestration",
            "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
        }
    )

    tracer_provider = TracerProvider(resource=resource)

    if grpc_endpoint:
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=grpc_endpoint))
        )
        print(f"[otel] OTLP gRPC exporter configured ({grpc_endpoint})")
    elif conn:
        if AzureMonitorTraceExporter is None:
            print(
                "Warning: Azure Monitor exporter not installed. "
                "Install with: pip install azure-monitor-opentelemetry-exporter",
            )
            tracer_provider.add_span_processor(
                BatchSpanProcessor(ConsoleSpanExporter())
            )
        else:
            tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    AzureMonitorTraceExporter.from_connection_string(conn)
                )
            )
            print("[otel] Azure Monitor trace exporter configured")
    else:
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        print("[otel] Console span exporter configured")
        print(
            "[otel] Set APPLICATION_INSIGHTS_CONNECTION_STRING to export to Application Insights "
            "instead of the console",
        )

    trace.set_tracer_provider(tracer_provider)


api_config = _resolve_api_config()
_set_capture_env(api_config.provider, api_config.base_url)
_configure_otel()
OpenAIAgentsInstrumentor().instrument(
    tracer_provider=trace.get_tracer_provider(),
    capture_message_content="span_and_event",
    agent_name="Weekend Planner",
    base_url=api_config.base_url,
    system=api_config.provider,
)

client = api_config.build_client()
set_default_openai_client(client)
set_tracing_disabled(False)


def _chat_model() -> OpenAIChatCompletionsModel:
    """Return the chat completions model used for weekend planning."""

    return OpenAIChatCompletionsModel(model=api_config.model_name, openai_client=client)


SUNNY_WEATHER_PROBABILITY = 0.05


@function_tool
def get_weather(city: str) -> dict[str, object]:
    """Fetch mock weather information for the requested city."""

    logger.info("Getting weather for %s", city)
    if random.random() < SUNNY_WEATHER_PROBABILITY:
        return {"city": city, "temperature": 72, "description": "Sunny"}
    return {"city": city, "temperature": 60, "description": "Rainy"}


@function_tool
def get_activities(city: str, date: str) -> list[dict[str, object]]:
    """Return mock activities for the supplied city and date."""

    logger.info("Getting activities for %s on %s", city, date)
    return [
        {"name": "Hiking", "location": city},
        {"name": "Beach", "location": city},
        {"name": "Museum", "location": city},
    ]


@function_tool
def get_current_date() -> str:
    """Return the current date as YYYY-MM-DD."""

    logger.info("Getting current date")
    return datetime.now().strftime("%Y-%m-%d")


ENGLISH_WEEKEND_PLANNER = Agent(
    name="Weekend Planner (English)",
    instructions=(
        "You help English-speaking travelers plan their weekends. "
        "Use the available tools to gather the weekend date, current weather, and local activities. "
        "Only recommend activities that align with the weather and include the date in your final response."
    ),
    tools=[get_weather, get_activities, get_current_date],
    model=_chat_model(),
)

# cSpell:disable
SPANISH_WEEKEND_PLANNER = Agent(
    name="Planificador de fin de semana (Español)",
    instructions=(
        "Ayudas a viajeros hispanohablantes a planificar su fin de semana. "
        "Usa las herramientas disponibles para obtener la fecha, el clima y actividades locales. "
        "Recomienda actividades acordes al clima e incluye la fecha del fin de semana en tu respuesta."
    ),
    tools=[get_weather, get_activities, get_current_date],
    model=_chat_model(),
)

TRIAGE_AGENT = Agent(
    name="Weekend Planner Triage",
    instructions=(
        "Revisa el idioma del viajero. "
        "Si el mensaje está en español, realiza un handoff a 'Planificador de fin de semana (Español)'. "
        "De lo contrario, usa 'Weekend Planner (English)'."
    ),
    handoffs=[SPANISH_WEEKEND_PLANNER, ENGLISH_WEEKEND_PLANNER],
    model=_chat_model(),
)
# cSpell:enable


def _root_span_name(provider: str) -> str:
    return f"weekend_planning_session[{provider}]"


def _apply_weekend_semconv(
    span: trace.Span,
    *,
    user_text: str,
    final_text: str,
    conversation_id: str | None,
    response_id: str,
    final_agent_name: str | None,
    success: bool,
) -> None:
    parsed = urlparse(api_config.base_url)
    if parsed.hostname:
        span.set_attribute("server.address", parsed.hostname)
    if parsed.port:
        span.set_attribute("server.port", parsed.port)

    span.set_attribute("gen_ai.operation.name", "invoke_agent")
    span.set_attribute("gen_ai.provider.name", api_config.provider)
    span.set_attribute("gen_ai.request.model", api_config.model_name)
    span.set_attribute("gen_ai.output.type", "text")
    span.set_attribute("gen_ai.response.model", api_config.model_name)
    span.set_attribute("gen_ai.response.id", response_id)
    span.set_attribute(
        "gen_ai.response.finish_reasons",
        ["stop"] if success else ["error"],
    )

    if conversation_id:
        span.set_attribute("gen_ai.conversation.id", conversation_id)
    if TRIAGE_AGENT.instructions:
        span.set_attribute("gen_ai.system_instructions", TRIAGE_AGENT.instructions)
    if final_agent_name:
        span.set_attribute("gen_ai.agent.name", final_agent_name)
    else:
        span.set_attribute("gen_ai.agent.name", TRIAGE_AGENT.name)
    if user_text:
        span.set_attribute(
            "gen_ai.input.messages",
            json.dumps([{"role": "user", "content": user_text}]),
        )
    if final_text:
        span.set_attribute(
            "gen_ai.output.messages",
            json.dumps([{"role": "assistant", "content": final_text}]),
        )


def _extract_user_text(request: CreateResponse) -> str:
    """Extract the first user text input from the request body."""

    input = request.get("input")
    if not input:
        return ""

    first = input[0]
    content = first.get("content", None) if isinstance(first, dict) else first
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        for item in content:
            text = item.get("text", None)
            if text:
                return text
    return ""


def _stream_final_text(final_text: str, context: AgentRunContext):
    """Yield streaming events for the provided final text."""

    async def _async_stream():
        assembled = ""
        yield ResponseCreatedEvent(response=OpenAIResponse(output=[]))
        item_id = context.id_generator.generate_message_id()
        yield ResponseOutputItemAddedEvent(
            output_index=0,
            item=ResponsesAssistantMessageItemResource(
                id=item_id,
                status="in_progress",
                content=[ItemContentOutputText(text="", annotations=[])],
            ),
        )

        words = final_text.split(" ")
        for idx, token in enumerate(words):
            piece = token if idx == len(words) - 1 else token + " "
            assembled += piece
            yield ResponseTextDeltaEvent(output_index=0, content_index=0, delta=piece)

        yield ResponseTextDoneEvent(output_index=0, content_index=0, text=assembled)
        yield ResponseCompletedEvent(
            response=OpenAIResponse(
                metadata={},
                temperature=0.0,
                top_p=0.0,
                user="user",
                id=context.response_id,
                created_at=datetime.now(timezone.utc),
                output=[
                    ResponsesAssistantMessageItemResource(
                        id=item_id,
                        status="completed",
                        content=[ItemContentOutputText(text=assembled, annotations=[])],
                    )
                ],
            )
        )

    return _async_stream()


def dump(title: str, payload: object) -> None:
    """Pretty print helper for the tracing demo."""

    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2))


def run_content_capture_demo() -> None:
    """Simulate an agent workflow using the tracing helpers without calling an API."""

    itinerary_prompt = [
        {"role": "system", "content": "Help travelers plan memorable weekends."},
        {"role": "user", "content": "I'm visiting Seattle this weekend."},
    ]
    tool_args = {"city": "Seattle", "date": "2025-05-17"}
    tool_result = {
        "forecast": "Light rain, highs 60°F",
        "packing_tips": ["rain jacket", "waterproof shoes"],
    }

    with tracing_trace("weekend-planner-simulation"):
        with tracing_agent_span(name="weekend_planner_demo") as agent:
            dump(
                "Agent span started",
                {"span_id": agent.span_id, "trace_id": agent.trace_id},
            )

            with tracing_generation_span(
                input=itinerary_prompt,
                output=[
                    {
                        "role": "assistant",
                        "content": (
                            "Day 1 explore Pike Place Market, Day 2 visit the Museum of Pop Culture, "
                            "Day 3 take the Bainbridge ferry if weather allows."
                        ),
                    }
                ],
                model=api_config.model_name,
                usage={
                    "input_tokens": 128,
                    "output_tokens": 96,
                    "total_tokens": 224,
                },
            ):
                pass

            with tracing_function_span(
                name="get_weather",
                input=json.dumps(tool_args),
                output=tool_result,
            ):
                pass

    print("\nWorkflow complete – spans exported to the configured OTLP endpoint.")


class WeekendPlannerContainer(FoundryCBAgent):
    """Container entry point that surfaces the weekend planner agent via FoundryCBAgent."""

    async def agent_run(self, context: AgentRunContext):
        request = context.request
        user_text = _extract_user_text(request)

        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(_root_span_name(api_config.provider)) as span:
            span.set_attribute("user.request", user_text)
            span.set_attribute("api.host", os.getenv("API_HOST", "github"))
            span.set_attribute("model.name", api_config.model_name)
            span.set_attribute("agent.name", TRIAGE_AGENT.name)
            span.set_attribute("triage.languages", "en,es")

            try:
                result = await Runner.run(TRIAGE_AGENT, input=user_text)
                final_text = str(result.final_output or "")
                span.set_attribute(
                    "agent.response", final_text[:500] if final_text else ""
                )
                final_agent = getattr(result, "last_agent", None)
                if final_agent and getattr(final_agent, "name", None):
                    span.set_attribute("agent.final", final_agent.name)
                span.set_attribute("request.success", True)
                _apply_weekend_semconv(
                    span,
                    user_text=user_text,
                    final_text=final_text,
                    conversation_id=context.conversation_id,
                    response_id=context.response_id,
                    final_agent_name=getattr(final_agent, "name", None),
                    success=True,
                )
                logger.info("Weekend planning completed successfully")
            except Exception as exc:  # pragma: no cover - defensive logging path
                span.record_exception(exc)
                span.set_attribute("request.success", False)
                span.set_attribute("error.type", exc.__class__.__name__)
                logger.error("Error during weekend planning: %s", exc)
                final_text = f"Error running agent: {exc}"
                _apply_weekend_semconv(
                    span,
                    user_text=user_text,
                    final_text=final_text,
                    conversation_id=context.conversation_id,
                    response_id=context.response_id,
                    final_agent_name=None,
                    success=False,
                )

        if request.get("stream", False):
            return _stream_final_text(final_text, context)

        response = OpenAIResponse(
            metadata={},
            temperature=0.0,
            top_p=0.0,
            user="user",
            id=context.response_id,
            created_at=datetime.now(timezone.utc),
            output=[
                ResponsesAssistantMessageItemResource(
                    id=context.id_generator.generate_message_id(),
                    status="completed",
                    content=[ItemContentOutputText(text=final_text, annotations=[])],
                )
            ],
        )
        return response


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    try:
        if RUN_MODE == "demo":
            run_content_capture_demo()
        else:
            WeekendPlannerContainer().run()
    finally:
        trace.get_tracer_provider().shutdown()

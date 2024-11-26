import argparse
import json
import logging
import os
from opentelemetry import trace
from dotenv import load_dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
from azure.ai.evaluation import RelevanceEvaluator
from ask_wiki import ask_wiki
from opentelemetry.trace.span import NonRecordingSpan
from gen_ai_trace import gen_ai_trace
from opentelemetry.trace import get_tracer, SpanContext
from pprint import pprint

load_dotenv()

logger = logging.getLogger(__name__)

configure_azure_monitor(connection_string=os.environ["APPINSIGHTS_CONNECTION_STRING"])

tracer = get_tracer("AskWikiApp")

model_config = {
    "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
    "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
}

def add_evaluations(query, response):
    relevance_eval = RelevanceEvaluator(model_config=model_config)
    relevance_result = relevance_eval(
        query=query,
        response=response["response"],
        context=response["context"],
    )

    # Adding evaluation results to the span
    span_context = SpanContext(
        trace_id=response["metadata"]["trace_id"],
        span_id=response["metadata"]["span_id"],
        trace_flags=response["metadata"]["trace_flags"],
        is_remote=True,
    )
    with trace.use_span(NonRecordingSpan(span_context)):
        logger.warning("Test Evaluation",
                       extra={"gen_ai.evaluation.score": json.dumps(relevance_result["gpt_relevance"]),
                              "gen_ai.response.id": response["metadata"]["response_id"],
                              "event.name": "gen_ai.evaluation.relevance"})


def run_ask_wiki(query: str):
    # tracer = trace.get_tracer("AskWikiAppTracing")
    # with tracer.start_as_current_span(name="AppTracing") as parent:
    response = ask_wiki(query=query)
    add_evaluations(query, response)
    return response


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("--query", type=str, help="Query for ask wiki application", default="How do you make pancakes?")

    # Parse the arguments
    args = parser.parse_args()

    OpenAIInstrumentor().instrument()
    response = run_ask_wiki(args.query)
    pprint("Response from ask wiki")
    pprint(response)
    pprint("Finished running ask wiki")
    OpenAIInstrumentor().uninstrument()


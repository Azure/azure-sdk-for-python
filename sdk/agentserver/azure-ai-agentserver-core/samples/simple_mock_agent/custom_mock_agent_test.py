# mypy: ignore-errors
import datetime

from azure.ai.agentserver.core import AgentRunContext, FoundryCBAgent
from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponseCompletedEvent,
    ResponseCreatedEvent,
    ResponseOutputItemAddedEvent,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)


def stream_events(text: str, context: AgentRunContext):
    item_id = context.id_generator.generate_message_id()

    assembled = ""
    yield ResponseCreatedEvent(response=OpenAIResponse(output=[]))
    yield ResponseOutputItemAddedEvent(
        output_index=0,
        item=ResponsesAssistantMessageItemResource(
            id=item_id,
            status="in_progress",
            content=[
                ItemContentOutputText(
                    text="",
                    annotations=[],
                )
            ],
        ),
    )
    for i, token in enumerate(text.split(" ")):
        piece = token if i == len(text.split(" ")) - 1 else token + " "
        assembled += piece
        yield ResponseTextDeltaEvent(output_index=0, content_index=0, delta=piece)
    # Done with text
    yield ResponseTextDoneEvent(output_index=0, content_index=0, text=assembled)
    yield ResponseCompletedEvent(
        response=OpenAIResponse(
            metadata={},
            temperature=0.0,
            top_p=0.0,
            user="me",
            id=context.response_id,
            created_at=datetime.datetime.now(),
            output=[
                ResponsesAssistantMessageItemResource(
                    id=item_id,
                    status="completed",
                    content=[
                        ItemContentOutputText(
                            text=assembled,
                            annotations=[],
                        )
                    ],
                )
            ],
        )
    )


async def agent_run(context: AgentRunContext):
    agent = context.request.get("agent")
    print(f"agent:{agent}")

    if context.stream:
        return stream_events(
            "I am mock agent with no intelligence in stream mode.", context
        )

    # Build assistant output content
    output_content = [
        ItemContentOutputText(
            text="I am mock agent with no intelligence.",
            annotations=[],
        )
    ]

    response = OpenAIResponse(
        metadata={},
        temperature=0.0,
        top_p=0.0,
        user="me",
        id=context.response_id,
        created_at=datetime.datetime.now(),
        output=[
            ResponsesAssistantMessageItemResource(
                id=context.id_generator.generate_message_id(),
                status="completed",
                content=output_content,
            )
        ],
    )
    return response


my_agent = FoundryCBAgent(project_endpoint="mock-endpoint")
my_agent.agent_run = agent_run

if __name__ == "__main__":
    my_agent.run()

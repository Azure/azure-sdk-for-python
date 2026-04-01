import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import MessagesState

# Add the parent directory to the Python path to allow imports
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.retriever_tool import retriever_tool

load_dotenv()
deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
response_model = init_chat_model(f"azure_openai:{deployment_name}")


def generate_query_or_respond(state: MessagesState):
    """Call the model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
    """
    response = (
        response_model
        # highlight-next-line
        .bind_tools([retriever_tool]).invoke(state["messages"])
    )
    return {"messages": [response]}

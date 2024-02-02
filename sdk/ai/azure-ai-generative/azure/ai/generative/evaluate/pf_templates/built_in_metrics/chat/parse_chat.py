from promptflow import tool
import json


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def parse_chat(chat: list) -> dict:
    parsed_chat = {}
    chat_length = len(chat)
    questions = []
    answers = []
    retrieved_documents_per_chat = []

    for each_turn in chat:
        if "user" in each_turn and "assistant" in each_turn: # legacy rag-evaluation format
            question = each_turn["user"]["content"]
            answer = each_turn["assistant"]["content"]
            retrieved_documents = each_turn["retrieved_documents"]

            questions.append(question)
            answers.append(answer)
            retrieved_documents_per_chat.append(retrieved_documents)
        elif "role" in each_turn and "content" in each_turn: # updated chat-completion format
            persona = each_turn["role"]
            content = each_turn["content"]
            if persona == "user":
                questions.append(content)
            elif persona == "assistant":
                answers.append(content)
                retrieved_documents = json.dumps(each_turn["context"]["citations"])
                retrieved_documents_per_chat.append(retrieved_documents)
            
    parsed_chat["questions"] = questions
    parsed_chat['answers'] = answers
    parsed_chat['retrieved_documents'] = retrieved_documents_per_chat
    return parsed_chat

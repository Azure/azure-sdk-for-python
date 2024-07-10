from promptflow import tool
import json


@tool
def parse_chat(chat: list) -> dict:
    parsed_chat = {}
    questions = []
    answers = []
    retrieved_documents_per_chat = []

    for each_turn in chat:
        if "user" in each_turn and "assistant" in each_turn:
            question = each_turn["user"]["content"]
            answer = each_turn["assistant"]["content"]
            try:
                retrieved_documents = each_turn["retrieved_documents"]
            except KeyError:
                retrieved_documents = None

            questions.append(question)
            answers.append(answer)
            retrieved_documents_per_chat.append(retrieved_documents)
        elif "role" in each_turn and "content" in each_turn:
            persona = each_turn["role"]
            content = each_turn["content"]
            if persona == "user":
                questions.append(content)
            elif persona == "assistant":
                answers.append(content)
                try:
                    retrieved_documents = json.dumps(
                        each_turn["context"]["citations"])
                except KeyError:
                    retrieved_documents = None
                retrieved_documents_per_chat.append(retrieved_documents)

    parsed_chat["questions"] = questions
    parsed_chat['answers'] = answers
    parsed_chat['retrieved_documents'] = retrieved_documents_per_chat
    return parsed_chat

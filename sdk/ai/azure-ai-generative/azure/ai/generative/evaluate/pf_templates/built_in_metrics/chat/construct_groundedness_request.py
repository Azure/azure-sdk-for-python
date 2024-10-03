from promptflow import tool
import json
import ast


def normalize_user_text(user_text):
    return user_text.replace("'", "\\\"")


def construct_single_request(question: str,
                             answer: str,
                             context: dict = None) -> dict:
    metrics = ["generic_groundedness"]
    user_text = json.dumps({
        "question": question,
        "answer": answer,
        "context": context})
    parsed_user_text = normalize_user_text(user_text)
    request_body = {"UserTextList": [parsed_user_text],
                    "AnnotationTask": "groundedness",
                    "MetricList": metrics}
    return request_body


@tool
def construct_groundedness_requests(parsed_chat: dict) -> str:
    num_turns = len(parsed_chat["questions"])
    request_bodies = []
    for i in range(num_turns):
        question = parsed_chat["questions"][i]
        answer = parsed_chat["answers"][i]
        try:
            retrieved_documents = ast.literal_eval(
                parsed_chat["retrieved_documents"][i])
        except Exception:
            retrieved_documents = [
                parsed_chat["retrieved_documents"][i]]
        context = {"citations": retrieved_documents}
        request = construct_single_request(question,
                                           answer,
                                           context)
        request_bodies.append(request)
    return request_bodies

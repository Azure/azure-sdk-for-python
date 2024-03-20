from promptflow import tool
import json


def normalize_user_text(user_text):
    return user_text.replace("'", "\\\"")


# The inputs section will change based on the arguments
# of the tool function, after you save the code
# Adding type to arguments and return value will help
# the system show the types properly
# Please update the function name/signature per need
@tool
def construct_request(question: str, answer:str, context: str) -> dict:
    metrics = ["generic_groundedness"]
    user_text = json.dumps({"question": question, 
                 "answer": answer,
                 "context": context})
    parsed_user_text = normalize_user_text(user_text)
    request_body = {"UserTextList": [parsed_user_text],
                    "AnnotationTask": "groundedness",
                    "MetricList":metrics}
    return request_body

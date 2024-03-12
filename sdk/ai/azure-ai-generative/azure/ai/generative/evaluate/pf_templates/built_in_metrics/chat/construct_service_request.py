from promptflow import tool
import json

def parse_chat(user_text: list):
    parsed_chat = []
    for turn in user_text:
        try:
            role = turn["role"]
            content = turn["content"]
            content_str = "<" + role + ">" + content + "</>\n"
        except KeyError:
            content_str = json.dumps(turn) + "\n"
        parsed_chat.append(content_str)
    return "{\"conversation\": \"" + "".join(parsed_chat) + "\"}"
        
def normalize_user_text(user_text):
    return user_text.replace("'", "\\\"")

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def construct_request(user_text: list, selected_metrics: dict) -> dict:
    selected_safety_metrics = selected_metrics["safety_metrics"]
    metrics = [metric for metric in selected_safety_metrics if selected_safety_metrics[metric]]
    parsed_user_text = parse_chat(user_text)
    request_body = {"UserTextList": [parsed_user_text], 
                    "AnnotationTask": "content harm", 
                    "MetricList": metrics}
    return request_body

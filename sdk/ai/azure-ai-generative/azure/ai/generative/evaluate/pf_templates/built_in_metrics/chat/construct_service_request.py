from promptflow import tool
import json


def parse_chat(user_text: list):
    parsed_chat = []
    for turn in user_text:
        try:
            role = turn["role"]
            content = turn["content"]
            if role == "user":
                content_str = "<Human>" + content + "</>\n"
            elif role == "assistant":
                content_str = "<System>" + content + "</>\n"
            else:
                content_str = "<" + role + ">" + content + "</>\n"
        except KeyError:
            content_str = json.dumps(turn) + "\n"
        parsed_chat.append(content_str)
    return "".join(parsed_chat)


def normalize_user_text(user_text):
    return user_text.replace("'", "\\\"")


@tool
def construct_request(user_text: list, selected_metrics: dict) -> dict:
    selected_safety_metrics = selected_metrics["safety_metrics"]
    metrics = [metric.replace("_unfairness", "_fairness") for metric in
               selected_safety_metrics if selected_safety_metrics[metric]]
    parsed_user_text = parse_chat(user_text)
    request_body = {"UserTextList": [parsed_user_text],
                    "AnnotationTask": "content harm",
                    "MetricList": metrics,
                    "PromptVersion": "0.2"
                    }
    return request_body

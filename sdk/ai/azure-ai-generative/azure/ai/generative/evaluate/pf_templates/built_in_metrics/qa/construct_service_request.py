from promptflow import tool

def normalize_user_text(user_text):
    return user_text.replace("'", "\\\"")

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def construct_request(question: str, answer:str, selected_metrics: dict) -> dict:
    selected_safety_metrics = selected_metrics["safety_metrics"]
    metrics = [metric for metric in selected_safety_metrics if selected_safety_metrics[metric]]
    user_text = f"<Human>{question}</><System>{answer}</>"
    parsed_user_text = normalize_user_text(user_text)
    request_body = {"UserTextList": [parsed_user_text], "AnnotationTask": "content harm", "MetricList":metrics}
    return request_body

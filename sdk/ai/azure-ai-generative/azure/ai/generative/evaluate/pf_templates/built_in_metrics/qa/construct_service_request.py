from promptflow import tool
import json
### helping fuction to check if the user_text is chat
        
def normalize_user_text(user_text):
    return user_text.replace("'", "\\\"")

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def construct_request(question: str, answer:str, context: str, ground_truth: str, selected_metrics: dict) -> dict:
    selected_safety_metrics = selected_metrics["safety_metrics"]
    metrics = [metric for metric in selected_safety_metrics if selected_safety_metrics[metric]]
    user_text_json = {"question": question, "answer": answer, "context": context, "ground_truth": ground_truth}
    user_text = json.dumps(user_text_json)
    parsed_user_text = normalize_user_text(user_text)
    request_body = {"UserTextList": [parsed_user_text], "AnnotationTask": "content harm", "MetricList":metrics}
    #request_body = {"UserTextList": [user_text], "AnnotationTask": annotation_task}
    return request_body

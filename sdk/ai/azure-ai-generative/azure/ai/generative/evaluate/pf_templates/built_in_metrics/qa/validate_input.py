from promptflow import tool
from utils import is_valid_string

@tool
def validate_input(question: str, answer: str, context: str, ground_truth: str, selected_metrics: dict) -> dict:
    input_data = {"question": question, "answer": answer, "context": context, "ground_truth": ground_truth}
    expected_input_cols = set(input_data.keys())
    dict_metric_required_fields = {"gpt_groundedness": set(["answer", "context"]),
                                   "gpt_relevance": set(["question", "answer", "context"]),
                                   "gpt_coherence": set(["question", "answer"]),
                                   "gpt_similarity": set(["question", "answer", "ground_truth"]),
                                   "gpt_fluency": set(["question", "answer"]),
                                   "f1_score": set(["answer", "ground_truth"])
                                   }
    actual_input_cols = set()
    for col in expected_input_cols:
        if input_data[col] and is_valid_string(input_data[col]):
            actual_input_cols.add(col)
    selected_quality_metrics = selected_metrics["quality_metrics"]
    data_validation = {}
    for metric in selected_quality_metrics:
        data_validation[metric] = False
        if selected_quality_metrics[metric]:
            metric_required_fields = dict_metric_required_fields[metric]
            if metric_required_fields <= actual_input_cols:
                data_validation[metric] = True
    return data_validation

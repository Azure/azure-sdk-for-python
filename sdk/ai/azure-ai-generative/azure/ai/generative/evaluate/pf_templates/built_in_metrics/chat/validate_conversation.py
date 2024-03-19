from promptflow import tool
#from azureml.metrics.common import _validation
#from azureml.metrics.common.contract import Contract
#from azureml.metrics.common.exceptions import InvalidOperationException
from utils import filter_metrics, is_conversation_valid, is_conversation_valid_with_context

def is_metric_group_selected(selected_metrics: dict) -> dict:
    group_selected = {}
    for metric_group in selected_metrics:
        group_selected[metric_group] = False
        for metric in selected_metrics[metric_group]:
            if selected_metrics[metric_group][metric]:
                group_selected[metric_group] = True
                break
    return group_selected

                
# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def validate_conversation(chat: [], selected_metrics: dict) -> bool:
    is_group_selected = is_metric_group_selected(selected_metrics)

    # no quality metrics are selected
    if (not is_group_selected['rag_metrics']) and (not is_group_selected['non_rag_metrics']):
        print("no quality metrics selected. ")
        return {"non_rag_metrics": False,
            "rag_metrics": False}
    
    # check if chat format is valid
    #is_valid_chat = is_conversation_valid(chat)
    try:
        is_valid_chat = is_conversation_valid(chat)
    except:
        is_valid_chat = False
    
    # chat format is not valid
    if not is_valid_chat:
        print("chat format is not valid")
        return {"non_rag_metrics": False,
            "rag_metrics": False}

    non_rag_node = is_group_selected['non_rag_metrics'] and is_valid_chat
    rag_node = False
    if is_group_selected['rag_metrics'] and is_valid_chat:
        try:
            rag_node = is_conversation_valid_with_context(chat)
        except:
            rag_node = False
    print("non_rag_metrics:", non_rag_node, "rag_metrics:", rag_node)

    return {"non_rag_metrics": non_rag_node, "rag_metrics": rag_node}

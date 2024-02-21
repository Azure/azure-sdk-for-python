from promptflow import tool
from azureml.metrics.common import _validation
from azureml.metrics.common.contract import Contract
from azureml.metrics.common.exceptions import InvalidOperationException
from utils import filter_metrics

def is_conversation_valid(chat: [], selected_metrics: dict) -> bool:
    reference_code = "validate_conversation"
    name = "chat_format"
    # check if role and content keys exist in every turn
    _validation._check_chat_conversation([chat], name, reference_code=reference_code)

    # check if context/documents keys exist for rag evaluation
    rag_metrics = filter_metrics(selected_metrics["rag_metrics"])
    if len(rag_metrics) > 0:
        for turn_num, each_turn in enumerate(chat):
            # to accept legacy rag_evaluation format:
            # [{"user": {"content": "<user_content>"}, 
            #  "assistant": {"content": "<assistang_content>"}, 
            #  "retrieved_documents": "<retrieved_documents>"}]
            if "user" in each_turn and "assistant" in each_turn: # legancy rag_evaluation format
                Contract.assert_true("retrieved_documents" in each_turn, 
                    message = "Please ensure to have retrieved_documents key in each turn for rag_evaluation."
                        + " Please check turn_number: {}".format(turn_num),
                    target=name, log_safe=True, 
                    reference_code = reference_code)
            elif "role" in each_turn and each_turn["role"] == "assistant":
                #if "context" not in each_turn:
                Contract.assert_true("context" in each_turn, 
                    message = "Please ensure to have context key in assistant turn for rag_evaluation."
                        + " Please check turn_number: {}".format(turn_num),
                    target=name, log_safe=True, 
                    reference_code = reference_code)
                if "context" in each_turn: #and "citations" not in each_turn["context"]:
                    Contract.assert_true("citations" in each_turn["context"], 
                    message = "Please ensure to have citations key in assistant turn context for rag_evaluation."
                        + " Please check turn_number: {}".format(turn_num),
                    target=name, log_safe=True, 
                    reference_code = reference_code)
    return True
                
# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def validate_conversation(chat: [], selected_metrics: dict) -> bool:
    try:
        is_valid_chat = is_conversation_valid(chat, selected_metrics)
    except Exception:
        is_valid_chat = False
    return is_valid_chat

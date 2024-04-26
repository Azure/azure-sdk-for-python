from promptflow import tool
from utils import is_conversation_valid, is_conversation_valid_with_context


def is_metric_group_selected(selected_metrics: dict) -> dict:
    group_selected = {}
    for metric_group in selected_metrics:
        group_selected[metric_group] = False
        for metric in selected_metrics[metric_group]:
            if selected_metrics[metric_group][metric]:
                group_selected[metric_group] = True
                break
    return group_selected


@tool
def validate_conversation(chat: list[dict],
                          selected_metrics: dict) -> dict:
    is_group_selected = is_metric_group_selected(selected_metrics)
    num_turns = len(chat) / 2
    chat_validation = {
                "non_rag_metrics": False,
                "rag_metrics": False,
                "parse_chat": False,
                "num_turns": num_turns}

    # if no quality metrics are selected,
    # set both metric groups to False
    # set parse_chat to False
    if (not is_group_selected['rag_metrics']) \
            and (not is_group_selected['non_rag_metrics']):
        print("no quality metrics selected. ")
        return chat_validation

    # check if chat format is valid
    try:
        is_valid_chat = is_conversation_valid(chat)
    except Exception:
        is_valid_chat = False

    # chat format is not valid
    if not is_valid_chat:
        print("chat format is not valid")
        return chat_validation

    non_rag_node = is_group_selected['non_rag_metrics'] and is_valid_chat
    rag_node = False
    if is_group_selected['rag_metrics'] and is_valid_chat:
        try:
            rag_node = is_conversation_valid_with_context(chat)
        except Exception:
            rag_node = False
    parse_chat = non_rag_node \
        or (rag_node and selected_metrics['rag_metrics']["gpt_groundedness"])

    num_turns = len(chat)
    chat_validation["non_rag_metrics"] = non_rag_node
    chat_validation["rag_metrics"] = rag_node
    chat_validation["parse_chat"] = parse_chat

    return chat_validation

from promptflow import tool
import numpy as np
import constants

def format_rag_results(rag_results: dict, supported_metrics):
    result_per_chat = {}
    result_per_turn = {}
    if rag_results:
        #result_per_chat = rag_results['metrics']
        for metric, value in rag_results['artifacts'].items():
            result_per_chat[metric] = rag_results['metrics']["mean_" + metric]
            result_per_turn[metric] = {"reason": value['reason'], "score": value['score_per_turn']}
    for metric in supported_metrics:
        if metric not in result_per_turn:
            result_per_chat[metric] = np.nan
            result_per_turn[metric] = np.nan
    return {"results_per_turn": result_per_turn, "results_per_chat": result_per_chat}


def format_non_rag_results(non_rag_results: dict, supported_metrics):
    result_per_chat = {}
    result_per_turn = {}
    if non_rag_results:
        for metric in non_rag_results['artifacts']:
            result_per_chat[metric] = non_rag_results['metrics']['mean_' + metric]
        result_per_turn = non_rag_results['artifacts']
    for metric in supported_metrics:
        if metric not in result_per_turn:
            result_per_turn[metric] = np.nan
            result_per_chat[metric] = np.nan
    return {"results_per_turn": result_per_turn, "results_per_chat": result_per_chat}

def format_safety_results(safety_results: dict, supported_metrics):
    result_per_chat = {}
    if safety_results:
        result_per_chat = safety_results
    for metric in supported_metrics:
        if metric not in result_per_chat:
            result_per_chat[metric] = np.nan
            result_per_chat[metric + "_reasoning"] = np.nan
    return result_per_chat

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def concatenate_metrics(rag_results: dict, non_rag_results: dict, 
                       safety_results: dict,
                       selected_metrics: dict) -> dict:
    formatted_rag = format_rag_results(rag_results, selected_metrics['rag_metrics'])
    formatted_non_rag = format_non_rag_results(non_rag_results, selected_metrics['non_rag_metrics'])
    formatted_safety = format_safety_results(safety_results, selected_metrics['safety_metrics'])
    results = {}
    for key in ["results_per_turn", "results_per_chat"]:
        result_concat = formatted_rag[key].copy()
        result_concat.update(formatted_non_rag[key])
        if key == "results_per_chat":
            result_concat.update(formatted_safety)
        results[key] = result_concat
    return results
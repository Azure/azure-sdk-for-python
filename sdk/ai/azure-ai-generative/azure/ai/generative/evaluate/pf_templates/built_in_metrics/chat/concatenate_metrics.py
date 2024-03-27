from promptflow import tool
import numpy as np


def format_rag_results(rag_results: dict,
                       selected_metrics: dict,
                       num_turns: int):
    result_per_chat = {}
    result_per_turn = {}
    supported_metrics = selected_metrics["rag_metrics"]
    if rag_results:
        for metric, value in rag_results['artifacts'].items():
            try:
                result_per_chat[metric] = round(
                    rag_results['metrics']["mean_" + metric],
                    2)
                result_per_turn[metric] = {"reason": value['reason'][0],
                                           "score": value['score_per_turn'][0]}
            except KeyError:
                result_per_chat[metric] = np.nan
                result_per_turn[metric] = {"score": [np.nan] * int(num_turns)}
    for metric in supported_metrics:
        if metric not in result_per_turn:
            result_per_chat[metric] = np.nan
    return {"results_per_turn": result_per_turn,
            "results_per_chat": result_per_chat}


def format_non_rag_results(non_rag_results: dict,
                           selected_metrics: dict,
                           num_turns: int):
    result_per_chat = {}
    result_per_turn = {}
    supported_metrics = selected_metrics["non_rag_metrics"]
    if non_rag_results:
        for metric in non_rag_results['artifacts']:
            try:
                result_per_chat[metric] = round(
                    non_rag_results['metrics']['mean_' + metric],
                    2)
                result_per_turn[metric] = {
                    "score": non_rag_results['artifacts'][metric]}
            except Exception:
                result_per_chat[metric] = np.nan
                result_per_turn[metric] = {
                    "score": [np.nan] * int(num_turns)}

    for metric in supported_metrics:
        if metric not in result_per_turn:
            result_per_chat[metric] = np.nan
    return {"results_per_turn": result_per_turn,
            "results_per_chat": result_per_chat}


def format_safety_results(safety_results: dict, selected_metrics):
    result_per_chat = {}
    supported_metrics = selected_metrics["safety_metrics"]
    if safety_results:
        result_per_chat = safety_results
    for metric in supported_metrics:
        if metric not in result_per_chat:
            result_per_chat[metric] = np.nan
            result_per_chat[metric + "_reason"] = np.nan
            result_per_chat[metric + "_score"] = np.nan
    return result_per_chat


@tool
def concatenate_metrics(rag_results: dict, non_rag_results: dict,
                        safety_results: dict,
                        groundedness_results: list[dict],
                        selected_metrics: dict,
                        chat_validation: dict) -> dict:
    num_turns = chat_validation["num_turns"]
    formatted_rag = format_rag_results(rag_results,
                                       selected_metrics,
                                       num_turns)
    formatted_non_rag = format_non_rag_results(non_rag_results,
                                               selected_metrics,
                                               num_turns)
    formatted_safety = format_safety_results(safety_results,
                                             selected_metrics)
    results = {}
    for key in ["results_per_turn", "results_per_chat"]:
        result_concat = formatted_rag[key].copy()
        result_concat.update(formatted_non_rag[key])
        result_concat.update(groundedness_results[key])
        if key == "results_per_chat":
            result_concat.update(formatted_safety)
        results[key] = result_concat
    return results

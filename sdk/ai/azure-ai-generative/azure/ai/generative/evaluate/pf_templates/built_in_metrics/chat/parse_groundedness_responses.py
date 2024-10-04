from promptflow import tool
from typing import List
import numpy as np
import re
import ast


def parse_single_response(response: dict) -> list:
    parsed_response = []
    for key in response:
        harm_type = key.replace("generic", "gpt")
        parsed_harm_response = {}
        try:
            harm_response = ast.literal_eval(response[key])
        except Exception:
            harm_response = response[key]
        if harm_response != "" and isinstance(harm_response, dict):
            # check if "output" is one key in harm_response
            if "output" in harm_response:
                harm_response = harm_response["output"]

            # get content harm metric_value
            if 'label' in harm_response:
                metric_value = harm_response['label']
            else:
                metric_value = np.nan

            # get reasoning
            if "reasoning" in harm_response:
                reasoning = harm_response['reasoning']
            elif "reason" in harm_response:
                reasoning = harm_response['reason']
            else:
                reasoning = ""
        elif harm_response != "" and isinstance(harm_response, str):
            metric_value_match = re.findall(r"(\b[0-7])\b", harm_response)
            if metric_value_match:
                metric_value = int(metric_value_match[0])
            else:
                metric_value = np.nan
            reasoning = harm_response
        elif harm_response != "" and (isinstance(harm_response, int)
                                      or isinstance(harm_response, float)):
            if harm_response >= 0 and harm_response <= 7:
                metric_value = harm_response
            else:
                metric_value = np.nan
            reasoning = ""
        else:
            metric_value = np.nan
            reasoning = ""
        try:    
            parsed_harm_response[harm_type] = float(metric_value)
        except Exception:
            parsed_harm_response[harm_type] = np.nan
        parsed_harm_response[harm_type + "_reason"] = reasoning
        parsed_response.append(parsed_harm_response)
    return parsed_response


def parse_groundedness_llm_response(num_turns: int,
                                    llm_groundedness_response=None) -> dict:
    result_per_chat = {"gpt_groundedness": np.nan}
    result_per_turn = {}
    if llm_groundedness_response:
        for metric, value in llm_groundedness_response['artifacts'].items():
            try:
                result_per_chat[metric] = round(
                    llm_groundedness_response['metrics']["mean_" + metric],
                    2)
                result_per_turn[metric] = {"reason": value['reason'][0],
                                           "score": value['score_per_turn'][0]}
            except KeyError:
                result_per_chat[metric] = np.nan
                result_per_turn[metric] = {"score": [np.nan] * int(num_turns)}
    return {"results_per_turn": result_per_turn,
            "results_per_chat": result_per_chat}


@tool
def parse_response(selected_metrics: dict,
                   service_availability: dict,
                   chat_validation: dict,
                   llm_groundedness_response: dict = None,
                   batch_response: List[dict] = None) -> List[List[dict]]:
    groundedness_results = None
    result_per_chat = {}
    result_per_turn = {}
    num_turns = chat_validation["num_turns"]
    if service_availability["groundedness_service"]:
        parsed_responses = {}
        for single_response in batch_response:
            parsed_single_responses = parse_single_response(single_response)
            if parsed_single_responses:
                results = parsed_single_responses[0]
                for key in results:
                    if key in parsed_responses:
                        parsed_responses[key].append(results[key])
                    else:
                        parsed_responses[key] = [results[key]]
        for metric in parsed_responses:
            metric_name = metric.replace("_reason", "")
            values = parsed_responses[metric]
            if metric_name not in result_per_turn:
                result_per_turn[metric_name] = {}
            if "_reason" not in metric:
                metric_score = round(np.nanmean(values), 2)
                result_per_chat[metric_name] = metric_score
                result_per_turn[metric_name]["score"] = values
            else:
                result_per_turn[metric_name]["reason"] = values
        groundedness_results = {"results_per_turn": result_per_turn,
                                "results_per_chat": result_per_chat}
    elif service_availability["groundedness_prompt"]:
        groundedness_results = parse_groundedness_llm_response(
            num_turns, llm_groundedness_response)
    else:
        metric_name = "gpt_groundedness"
        result_per_chat = {metric_name: np.nan}
        if selected_metrics["rag_metrics"][metric_name]:
            result_per_turn = {metric_name:
                               {"score": [np.nan] * int(num_turns)}}
        groundedness_results = {"results_per_turn": result_per_turn,
                                "results_per_chat": result_per_chat}
    return groundedness_results

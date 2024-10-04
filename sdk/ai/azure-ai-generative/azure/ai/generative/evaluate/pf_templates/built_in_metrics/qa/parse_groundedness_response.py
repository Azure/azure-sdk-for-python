from promptflow import tool
from typing import List
import numpy as np
import re
import ast


def parse_single_sample(response: dict) -> list:
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
                try:
                    metric_value = int(harm_response['label'])
                except Exception:
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
        parsed_harm_response[harm_type] = metric_value
        parsed_harm_response[harm_type + "_reason"] = reasoning
        parsed_response.append(parsed_harm_response)
    return parsed_response


def parse_groundedness_llm_response(llm_groundedness_response=None) -> dict:
    item = {'name': 'gpt_groundedness',
            'score': llm_groundedness_response}
    if item['score']:
        try:
            score = item["score"]
            match = re.search(r'\d', score)
            if match:
                score = float(match.group())
            else:
                score = np.nan
        except Exception:
            score = np.nan
    else:
        score = np.nan
    return {"gpt_groundedness": score,
            "gpt_groundedness_reason": np.nan}


@tool
def parse_response(is_service_available: dict,
                   llm_groundedness_response: dict = None,
                   batch_response: List[dict] = None):
    parsed_single_sample_response = None
    if is_service_available["groundedness_service"]:
        if batch_response:
            single_sample_response = batch_response[0]
            parsed_single_sample_response = parse_single_sample(
                single_sample_response)[0]
    else:
        parsed_single_sample_response = \
            parse_groundedness_llm_response(llm_groundedness_response)

    return parsed_single_sample_response

from promptflow import tool
from typing import List
import numpy as np
import re

def parse_single_sample(response: dict, selected_metrics: dict) -> list:
    selected_label_keys = selected_metrics["safety_metrics"]
    parsed_response = []
    for key in response:
        if selected_label_keys[key]:
            harm_type = key#.replace("_flattened.md", "")
            parsed_harm_response = {}
            try:
                harm_response = eval(response[key])
            except NameError as e:
                # fix the eval error if there's "true" in the response
                m = re.findall("name \'(\w+)\' is not defined", str(e))
                if m:
                    for word in m:
                        response[key] = response[key].replace(word, word.title())
                    harm_response = eval(response[key])
                else:
                    harm_response = ""
            except:
                harm_response = response[key]
            if harm_response != "" and isinstance(harm_response, dict):
                ### check if "output" is one key in harm_response
                if "output" in harm_response:
                    harm_response = harm_response["output"]

                # get content harm metric_value
                if 'label' in harm_response:
                    #parsed_harm_response[harm_type] = harm_response['label']
                    metric_value = harm_response['label']
                elif 'valid' in harm_response:
                    metric_value = 0 if harm_response['valid'] else np.nan
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
            elif harm_response != "" and (isinstance(harm_response, int) or isinstance(harm_response, float)):
                if harm_response >= 0 and harm_response <= 7:
                    metric_value = harm_response
                else:
                    metric_value = np.nan
                reasoning = ""
            else:
                metric_value = np.nan
                reasoning = ""
            parsed_harm_response[harm_type] = metric_value
            parsed_harm_response["reasoning"] = reasoning
            parsed_response.append(parsed_harm_response)
    return parsed_response

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def parse_response(batch_response: List[dict], selected_label_keys: dict) -> List[List[dict]]:

    parsed_response = []
    for single_sample_response in batch_response:
        parsed_single_sample_response = parse_single_sample(single_sample_response, selected_label_keys)
        parsed_response.append(parsed_single_sample_response)
    return parsed_response
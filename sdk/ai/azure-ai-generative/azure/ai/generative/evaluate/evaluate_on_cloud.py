# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.resources.client import AIClient
from azure.ai.ml.identity import AzureMLOnBehalfOfCredential
from promptflow._sdk._constants import RunStatus
from azure.ai.generative.evaluate import evaluate
from promptflow.azure._pf_client import PFClient
import mlflow
import os, json
import pandas as pd
import tempfile, random, string

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data")
    parser.add_argument("--asset", default=None)

    return parser.parse_args()

def load_data(file_uri:string) -> pd.DataFrame:
    ### helping function to load from input file into dataframe
    file_type = file_uri.split('.')[-1].strip()
    if file_type not in ("csv", "jsonl"):
            return pd.DataFrame()
    if file_type == "csv":
        data = pd.read_csv(file_uri, sep=',')
    elif file_type == "jsonl":
        with open(file_uri) as f:
            data_jsonl = [eval(line) for line in f.readlines()]
        data = pd.DataFrame().from_records(data_jsonl)
    return data

def create_random_string(length:int) -> str:
   ### helping function to create random string with required length
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

class environment_parameter_parser:
    def __init__(self):
        self.config = self.get_config()
        self.eval_mapping, self.flow_mapping = self.get_col_mappings()
        self.metrics = self.get_target_metrics()
        self.task_type = self.get_task_type()
        self.gpt_model_deployment_name = self.get_gpt_model_deployment_name()
        self.embedding_model_deployment_name = self.get_embedding_model_deployment_name()
        self.validate_model_selection()

    def get_config(self):
        config =  {
          "subscription_id": os.getenv("SUBSCRIPTION_ID"),
          "resource_group": os.getenv("RESOURCE_GROUP"),
          "project_name": os.getenv("PROJECT_NAME")
        }
        return config


    def get_col_mappings(self):
        col_mapping_str = os.getenv("COL_MAPPING")
        col_mapping = eval(col_mapping_str.lower())
        EVAL_UI_COL_MAPPING = {
            'questions': 'question',
            'contexts': 'context',
            'y_pred': 'answer',
            'y_test': 'ground_truth'
        }
        eval_mapping = {}
        flow_mapping = {}

        ### parse column mappings for evaluation
        for key, val in EVAL_UI_COL_MAPPING.items():
            if val in col_mapping.keys():
                eval_mapping[key] = col_mapping[val]
        
        ### parse column mappings for prompt flow
        for key, value in col_mapping.items():
            if value.startswith('data'):
                flow_mapping[key] = "${" + value + "}"
        return eval_mapping, flow_mapping

    def get_target_metrics(self):
        """
        Valid metrics for QA and RAG_evaluation:
        QA_SET = {
            "bertscore", "exact_match", "f1_score",
            "ada_cosine_similarity",
            "gpt_similarity",
            "gpt_coherence",
            "gpt_relevance",
            "gpt_fluency",
            "gpt_groundedness",
        }

        RAG_EVALUATION = {"grounding_score", "retrieval_score", "generation_score"}
        """
        try:
            metrics_str = os.getenv("METRICS").lower()
            metrics = [metric.strip() for metric in metrics_str.split(',') if metric]
        except:
            metrics = None
        return metrics

    def get_variant_list(self):
        try:
            variants = os.getenv("VARIANT").lower()
            variant_list = ['${' + variant.strip() + '}' for variant in variants.split(',') if variant]
        except:
            variant_list = None
        return variant_list

    def get_task_type(self):
        return os.getenv("TASK_TYPE")
    
    def get_gpt_model_deployment_name(self):
        try:
            gpt_model = os.getenv("GPT_MODEL_DEPLOYMENT_NAME")
        except:
            gpt_model = None 
        return gpt_model 

    def get_embedding_model_deployment_name(self):
        try:
            embedding_model = os.getenv("EMBEDDING_MODEL_DEPLOYMENT_NAME")
        except:
            embedding_model = None 
        return embedding_model
    
    def validate_model_selection(self):
        if "ada_similarity" in self.metrics and not self.embedding_model_deployment_name:
            raise Exception("No embedding model is selected for ada_similarity evaluation.")
        if not self.metrics and not self.gpt_model_deployment_name:
            raise Exception('No GPT model is selected for GPT-assisted metric evaluation.')
        for metric in self.metrics:
            if "gpt" in metric and not self.gpt_model_deployment_name:
                raise Exception('No GPT model is selected for GPT-assisted metric evaluation.')


class promptflow_handler:
    def __init__(self, credential, env_parameters: environment_parameter_parser):
        self.pf_client = self.get_pf_client(credential, env_parameters.config)
        self.flow_mapping = env_parameters.flow_mapping
    
    def _set_promptflow_connection(self, config):
        import subprocess
        pf_config = f"""connection.provider=azureml:/subscriptions/{config['subscription_id']}/""" \
        + f"""resourceGroups/{config['resource_group']}/""" \
        + f"""providers/Microsoft.MachineLearningServices/workspaces/{config['project_name']}"""
        cmd = 'pf config set ' + pf_config
        
        pf_config_out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

    def get_pf_client(self, credential, config):
        self._set_promptflow_connection(config)
        pf_client = PFClient(credential, 
                            subscription_id=config['subscription_id'], 
                            resource_group_name=config['resource_group'], 
                            workspace_name=config['project_name']
                            )
        return pf_client
                
    def run(self, datafile, asset, variant=None):
        if not variant:
            variant_show_name = 'default'
        else:
            variant_show_name = variant[2:-1]
        ### run prompt flow with variant. if variant is None, run the default variant
        pf_run_result = self.pf_client.run(
                    flow=asset,
                    data=datafile,#data_file,
                    column_mapping=self.flow_mapping, 
                    variant=variant, #${node_name.variant_name}, e.g. "${summarize_text_content.variant_1}"
                    display_name="prompt_flow_run_" + variant_show_name,
                    stream=True
                )
        if pf_run_result.status == RunStatus.COMPLETED:
            pf_result_df = self.pf_client.get_details(pf_run_result.name)
            pf_result_postprocess = self.process_pf_result(pf_result_df)
            pf_result_postprocess['variant'] = variant_show_name
            return pf_result_postprocess
        else:
            raise Exception("the promptflow run status is not completed.")
        

    def process_pf_result(self, result_df: pd.DataFrame) -> pd.DataFrame:
        input_columns = [col for col in result_df.columns if col.startswith("inputs.")]
        output_columns = [col for col in result_df.columns if col.startswith("outputs.")]
        column_mapping = {col: col.replace("inputs.", "data.") for col in input_columns}
        column_mapping.update({col: col.replace("outputs.", "output.") for col in output_columns})
        
        result_df.rename(columns=column_mapping, inplace=True)
        return result_df

class evaluation_handler:
    def __init__(self, credential, env_parameters):
        self.env_parameters = env_parameters
        self.client = self.get_ai_client(credential)
        self.openai_parameters = self.get_openai_parameters()   
    
    def get_ai_client(self, credential):
        config = self.env_parameters.config
        return AIClient(credential=credential, subscription_id=config['subscription_id'], 
                      resource_group_name=config['resource_group'], project_name=config['project_name'])

    def get_openai_parameters(self):
        # retrieve openAI connection and set in environment
        default_aoai_connection = self.client.get_default_aoai_connection()
        default_aoai_connection.set_current_environment()
        model_deployment = self.env_parameters.gpt_model_deployment_name

        openai_params =  {
                "api_version": "2023-05-15",
                "api_base": os.getenv("OPENAI_API_BASE"),
                "api_type": "azure",
                "api_key" : os.getenv("OPENAI_API_KEY"),
                "deployment_id": model_deployment #DEFAULT_MODEL #chat_model_deployment
            }
        return openai_params

    def evaluate(self, data_eval_input: pd.DataFrame, evaluation_name="baseline_evaluation"):
        if data_eval_input.shape[0] == 0:
            raise Exception("Invalid Input: Evaluation Input is Empty!")
        openai_params = self.get_openai_parameters()
        
        #metrics_config = self.env_parameters.eval_mapping
        #metrics_config["openai_params"] = openai_params
        metrics = self.env_parameters.metrics

        openai_params = self.get_openai_parameters()
        metrics = self.env_parameters.metrics

        result = evaluate(
            evaluation_name=evaluation_name,
            data=data_eval_input,#csv_file_uri,
            task_type=self.env_parameters.task_type, # 'qa' only support task.question_answering
            data_mapping=self.env_parameters.eval_mapping,
            model_config = openai_params,
            metrics_list=metrics
            )
        return result 
 
def run_and_eval_flow(pf_handler: promptflow_handler, eval_handler: evaluation_handler, dataset: pd.DataFrame, asset:str):
    env_parameters = eval_handler.env_parameters
    variant_list = env_parameters.get_variant_list()
    
    eval_results = {}
    with tempfile.TemporaryDirectory() as tmpdir:

        ### write input data into a local jsonl file
        tmp_path = os.path.join(tmpdir, "test_data.jsonl")
        test_data = dataset.to_dict("records")
        with open(tmp_path, "w") as f:
            for line in test_data:
                f.write(json.dumps(line) + "\n")
        if variant_list:
            for variant in variant_list:
                pf_result = pf_handler.run(tmp_path, asset, variant)
                variant_show_name = variant[2:-1]
                evaluation_name = 'evaluation_' + variant_show_name + '_'+ create_random_string(5)
        
                eval_result = eval_handler.evaluate(pf_result, evaluation_name)

                eval_results[variant_show_name] = eval_result
        else:
            pf_result = pf_handler.run(tmp_path, asset)
            evaluation_name = "evaluation_default_" + create_random_string(5)
            eval_result = eval_handler.evaluate(pf_result, evaluation_name)
            eval_results["default"] = eval_result

    return eval_results

if __name__ == '__main__':

    ### start mlflow run
    run = mlflow.start_run()

    args = parse_args()
    data_file = args.data
    asset = args.asset
    
    data_df_input = load_data(data_file)

    credential = AzureMLOnBehalfOfCredential()

    env_parameters = environment_parameter_parser()
    eval_handler = evaluation_handler(credential, env_parameters)

    ### run prompt flow and evaluate
    ### if no prompt flow is provided, evaluate the input data
    results = {}
    if asset:
        pf = promptflow_handler(credential, env_parameters)
        results = run_and_eval_flow(pf, eval_handler, data_df_input, asset)
    else:
        column_mapping = {col: "data." + col for col in data_df_input.columns}
        data_eval_input = data_df_input.rename(columns=column_mapping)
        evaluation_name = 'evaluation_baseline'
        results[evaluation_name] = eval_handler.evaluate(data_eval_input, evaluation_name)
    mlflow.end_run()
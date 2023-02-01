import argparse
import json
import os
import shutil
import sys

from rcall.azureml import start_gpt3_run


def get_n_problems(config_json_path):
    path = os.path.join(config_json_path, "config.json")
    with open(path, "r") as f:
        config = json.load(f)

    return config["n_problems"]["train"]


if __name__ == "__main__":
    rank = os.environ["OMPI_COMM_WORLD_RANK"]
    node_count = os.environ["AZUREML_PARAMETER_Node_Count"]
    processes_per_node = os.environ["AZUREML_PARAMETER_Mpi_Process_Count_Per_Node"]
    print("node count {}, processes {}".format(node_count, processes_per_node))

    parser = argparse.ArgumentParser()
    parser.add_argument("--output_model")
    parser.add_argument("--input_dataset")
    parser.add_argument("--base_model")
    parser.add_argument("--lora_weights")
    parser.add_argument("--tuning_type")
    parser.add_argument("--engine")
    parser.add_argument("--n_epochs", type=int)
    parser.add_argument("--batch_size", type=int)
    parser.add_argument("--learning_rate_multiplier", type=float)
    parser.add_argument("--use_packing")
    args, unparsed = parser.parse_known_args()

    # validation
    assert args.base_model is not None
    assert args.output_model is not None

    totalgpus = int(node_count) * int(processes_per_node)
    pipe_depth = int(node_count)
    n_shards = int(totalgpus / pipe_depth)

    # pipe_depth = int(node_count) * int(processes_per_node)
    assert 96 % pipe_depth == 0

    n_problems = get_n_problems(args.input_dataset)
    max_total_steps = (int(n_problems) * args.n_epochs) / args.batch_size
    assert max_total_steps > 0

    encoding_path = args.base_model + "/encoding"
    base_model_path = args.base_model + "/200b_v2"

    arguments = [
        "--hps",
        "nest,200b_v2,finetune_v3,arch_v3",
        "--n_shards",
        n_shards,
        "--steps_per_save",
        500,
        "--steps_per_eval",
        20,
        "--lr_warmup_tokens",
        250000,
        "--anneal_lr_to_zero",
        "--seed",
        1,
        "--encoding_base_path",
        encoding_path,
        "--snapshot",
        base_model_path,
        "--gcs_root_logdir",
        args.output_model + "/gcs_root_logdir",
        "--gcs_backup_root",
        args.output_model + "/gcs_backup_logdir",
        "--name",
        "aml",
    ]

    print("pipe depth is ", pipe_depth)
    if args.tuning_type == "fine_tuning":
        print("Use gpt-3 raw")
        arguments += [
            "--pipe_depth",
            pipe_depth,
            "--attn_lora_dim",
            0,
        ]
    elif args.tuning_type == "lora":
        print("Use gpt-3 lora")
        arguments += [
            "--pipe_depth",
            pipe_depth,
            "--attn_lora_dim",
            32,
            "--n_ctx",
            256,
            "--max_n_ctx",
            256,
            "--dedicated_unembed",
            False,
        ]
        if args.lora_weights:
            print("Use provided model snapshot")
            arguments += ["--snapshot_lora", args.lora_weights]

    if args.n_epochs:
        print("max_epochs", args.n_epochs)
        arguments += ["--max_epochs", args.n_epochs]

    if args.batch_size:
        print("examples_per_global_batch", args.batch_size)
        arguments += ["--examples_per_global_batch", args.batch_size]
        arguments += ["--eval_examples_per_global_batch", 20 * args.batch_size]

    if args.learning_rate_multiplier:
        print("lr", args.learning_rate_multiplier)
        arguments += ["--lr", args.learning_rate_multiplier]

    if args.use_packing == "True":
        arguments += ["--dataset_hparams", '{"pack_context":True}']

    print("arguments", arguments)
    for arg in arguments:
        sys.argv.append(str(arg))

    # remove unused args
    remove_list = [
        "--output_model",
        "--base_model",
        "--lora_weights",
        "--tuning_type",
        "--engine",
        "--n_epochs",
        "--batch_size",
        "--learning_rate_multiplier",
        "--use_packing",
    ]
    for argument in remove_list:
        if argument in sys.argv:
            idx = sys.argv.index(argument)
            sys.argv.pop(idx)  # remove key
            sys.argv.pop(idx)  # remove value

    start_gpt3_run()

    ## copy base weights and encodings to outputs
    if rank == "0":
        upload_dir = args.output_model + "/encoding"
        if not os.path.exists(upload_dir):
            print("Upload encoding")
            shutil.copytree(args.base_model + "/encoding", upload_dir)

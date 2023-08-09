# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import os
import pandas as pd
import numpy as np
import argparse
import yaml
import json
import re
import mltable


def normalize_path_value(
    input_val: str,
) -> str:
    return re.sub('\.|\s|\\\\|\||\*|/|\<|\>|\?|:|"', "_", input_val)


def dump_df_to_mltable(
    input_df: pd.DataFrame,
    target_path: str,
    partition_cols=[],
):
    if len(partition_cols) > 0:
        for item in partition_cols:
            if str(item) not in input_df.columns:
                raise Exception("No target column found from input tabular data")
        has_partition = True
    else:
        has_partition = False

    partitioned_file_name = "partitioned_data.csv"

    # Dump df to target path
    if has_partition:
        for group_name, group_df in input_df.groupby(partition_cols):
            if hasattr(group_name, "__iter__"):
                relative_path = os.path.join(target_path, *[normalize_path_value(str(e)) for e in group_name])
            else:
                relative_path = os.path.join(target_path, str(group_name))

            if not os.path.exists(relative_path):
                os.makedirs(relative_path)

            output_path = os.path.join(relative_path, partitioned_file_name)
            group_df.drop(columns=partition_cols, errors="ignore").to_csv(output_path, index=False)
    else:
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        output_path = os.path.join(target_path, partitioned_file_name)
        input_df.to_csv(output_path, index=False)

    # Create ML table artifact object
    mltable_path = os.path.join(target_path, "MLTable")
    mltable_dic = {
        "type": "mltable",
        "paths": [],
        "transformations": [
            {
                "read_delimited": {
                    "delimiter": ",",
                    "encoding": "ascii",
                    "header": "all_files_same_headers",
                    "empty_as_string": False,
                    "include_path_column": True,
                },
            },
        ],
    }

    if has_partition:
        partition_format_str = ""
        partition_key_droplist = ["Path", "file_name", "extension"]

        for col_name in partition_cols:
            partition_format_str = partition_format_str + "{" + col_name + "}" + "/"

        partition_format_str = partition_format_str + "{file_name}.{extension}"
        mltable_dic["paths"].append({"pattern": "./**/*.csv"})
        mltable_dic["transformations"].append(
            {
                "extract_columns_from_partition_format": {"partition_format": partition_format_str},
            }
        )
        mltable_dic["transformations"].append({"drop_columns": partition_key_droplist})
    else:
        mltable_dic["paths"].append({"pattern": "./*.csv"})

    # Dump ML table artifact object to file
    with open(mltable_path, "w") as yaml_file:
        yaml.dump(mltable_dic, yaml_file, default_flow_style=False)


parser = argparse.ArgumentParser()
parser.add_argument("--data_source", type=str)
parser.add_argument("--partition_keys", type=str)
parser.add_argument("--tabular_output_data", type=str)

args, _ = parser.parse_known_args()

try:
    input_df = pd.read_csv(args.data_source)
except:
    raise Exception("Can not load input data as csv tabular data.")

partition_cols = args.partition_keys.split(",")
dump_df_to_mltable(
    input_df=input_df,
    target_path=args.tabular_output_data,
    partition_cols=partition_cols,
)

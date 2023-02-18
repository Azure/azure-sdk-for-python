# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# This file contains mldesigner decorator-produced components
# that are used within node constructors. Keep imports and 
# general complexity in this file to a minimum.

from mldesigner import command_component, Output

@command_component
def merge_comp(output: Output, **kwargs):
    for k, v in kwargs.items():
        print(k)
        print(v)

def save_mltable_yaml(path, mltable_paths):
    import os
    import yaml
    path = os.path.abspath(path)

    if os.path.isfile(path):
        raise ValueError(f'The given path {path} points to a file.')

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    save_path = os.path.join(path, 'MLTable')

    # mltable_yaml_dict = yaml.dump({"paths": mltable_paths}, default_)
    # mltable_yaml_dict[_PATHS_KEY] = self.paths
    with open(save_path, 'w') as f:
        yaml.dump({"paths": mltable_paths}, f)


@command_component(environment="azureml:test_fl_command_component@latest")
def aggregate_output(aggregated_output: Output(type="mltable"), **kwargs):
    print("Aggregated Output {}".format(aggregated_output))
    path_list = []
    for k, v in kwargs.items():
        print("Input name is {}".format(k))
        print("Input value is {}".format(v))
        path_list.append({"folder": v})

    save_mltable_yaml(aggregated_output, path_list)

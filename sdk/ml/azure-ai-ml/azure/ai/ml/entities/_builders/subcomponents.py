# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# This file contains mldesigner decorator-produced components
# that are used within node constructors. Keep imports and 
# general complexity in this file to a minimum.

from mldesigner import command_component, Output


def save_mltable_yaml(path, mltable_paths):
    import os
    import yaml
    path = os.path.abspath(path)

    if os.path.isfile(path):
        raise ValueError(f'The given path {path} points to a file.')

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    save_path = os.path.join(path, 'MLTable')
    mltable_file_content = "\n".join(["paths:"] + [f"- folder : {path}" for path in mltable_paths])

    # mltable_yaml_dict = yaml.dump({"paths": mltable_paths}, default_)
    # mltable_yaml_dict[_PATHS_KEY] = self.paths
    with open(save_path, 'w') as f:
        f.write(mltable_file_content)


@command_component()
def aggregate_output(aggregated_output: Output(type="mltable"), **kwargs):
    print("Aggregated Output {}".format(aggregated_output))
    path_list = [k for k,v in kwargs.items()]
    save_mltable_yaml(aggregated_output, path_list)

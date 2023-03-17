import argparse
import os

from mldesigner._component_executor import ExecutorBase

parser = argparse.ArgumentParser()
parser.add_argument("--component_in_number", type=int)
parser.add_argument("--component_in_number_1", type=int)
parser.add_argument("--component_in_path", type=str)
parser.add_argument("--output_in_path", type=str)
parser.add_argument("--output_in_number", type=str)


args = parser.parse_args()

lines = [
    f"component_in_number: {args.component_in_number}",
    f"component_in_number_1: {args.component_in_number_1}",
    f"component_in_path: {args.component_in_path}",
]

if args.component_in_number is not None:
    component_in_number = args.component_in_number
elif os.path.exists(os.path.join(args.component_in_path, "output.txt")):
    with open(os.path.join(args.component_in_path, "output.txt"), "r") as file:
        content = file.read()
        try:
            component_in_number = int(content)
        except Exception:
            component_in_number = args.component_in_number
else:
    component_in_number = 0

output_in_num = component_in_number - 1

with open(os.path.join(args.output_in_path, "output.txt"), "w") as file:
    file.write(str(output_in_num))

control_output_content = '{"is_number_larger_than_zero": "%s", "output_in_number": "%s"}' % (
    str(output_in_num > 0),
    output_in_num,
)
ExecutorBase._write_control_outputs_to_run_history(control_output_content=control_output_content)

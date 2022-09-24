import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--component_in_number", type=int)
parser.add_argument("--component_in_number_1", type=int)
parser.add_argument("--component_in_path", type=str)
parser.add_argument("--output_in_number", type=str)
parser.add_argument("--output_in_path", type=str)
parser.add_argument("--is_number_larger_than_zero", type=str)


args = parser.parse_args()

lines = [
    f"component_in_number: {args.component_in_number}",
    f"component_in_number_1: {args.component_in_number_1}",
    f"component_in_path: {args.component_in_path}",
]

output_in_num = args.component_in_number - 1

with open(args.component_in_path, "r") as file:
    content = file.readlines()
content.append(str(output_in_num))

with open(args.output_in_number, "w") as file:
    file.write(str(output_in_num))

with open(args.output_in_path, "w") as file:
    file.writelines(content)

with open(args.is_number_larger_than_zero, "w") as file:
    file.write(output_in_num > 0)

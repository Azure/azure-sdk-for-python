import argparse

parser = argparse.ArgumentParser("main")
parser.add_argument("--component_in_number", type=int, help="component_in_number")

args = parser.parse_args()

print ("hello world...")

lines = [
    f'component_in_number: {args.component_in_number}',
]

for line in lines:
    print(line)

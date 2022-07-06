import argparse
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--componentC_input", type=str)
parser.add_argument("--componentC_output", type=str)

print ("Hello Python World...\nI'm componentC :-)")

args = parser.parse_args()

print("componentC_input path: %s" % args.componentC_input)
print("componentC_output path: %s" % args.componentC_output)

print("files in input path: ")
arr = os.listdir(args.componentC_input)
print(arr)

for filename in arr:
    print ("reading file: %s ..." % filename)
    with open(os.path.join(args.componentC_input, filename), 'r') as handle:
        print (handle.read())

cur_time_str = datetime.now().strftime("%b-%d-%Y-%H-%M-%S")

print("Writing file: %s" % os.path.join(args.componentC_output,"file-" + cur_time_str + ".txt"))
with open(os.path.join(args.componentC_output,"file-" + cur_time_str + ".txt"), "wt") as text_file:
    print(f"Logging date time: {cur_time_str}", file=text_file)


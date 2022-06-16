import argparse
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import os

parser = argparse.ArgumentParser("train")
parser.add_argument("--training_data", type=str, help="Path to training data")
parser.add_argument("--max_epocs", type=int, help="Max # of epocs for the training")
parser.add_argument("--learning_rate", type=float, help="Learning rate")
parser.add_argument("--learning_rate_schedule", type=str, help="Learning rate schedule")
parser.add_argument("--model_output", type=str, help="Path of output model")
parser.add_argument("--reports", type=str, help="Path of reports")

args = parser.parse_args()

print ("hello training world...")

lines = [
    f'Training data path: {args.training_data}',
    f'Max epocs: {args.max_epocs}',
    f'Learning rate: {args.learning_rate}',
    f'Learning rate: {args.learning_rate_schedule}',
    f'Model output path: {args.model_output}',
    f'Model output path: {args.reports}'
]

for line in lines:
    print(line)

print("mounted_path files: ")
arr = os.listdir(args.training_data)
print(arr)

for filename in arr:
    print ("reading file: %s ..." % filename)
    with open(os.path.join(args.training_data, filename), 'r') as handle:
        print (handle.read())


# Do the train and save the trained model as a file into the output folder.
# Here only output a dummy data for demo.
curtime = datetime.now().strftime("%b-%d-%Y %H:%M:%S")
model = f"This is a dummy model with id: {str(uuid4())} generated at: {curtime}\n"
(Path(args.model_output) / 'model.txt').write_text(model)

curtime = datetime.now().strftime("%b-%d-%Y %H:%M:%S")
model = f"This is a dummy report with id: {str(uuid4())} generated at: {curtime}\n"
(Path(args.reports) / 'report.txt').write_text(model)

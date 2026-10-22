import argparse
from pathlib import Path

parser = argparse.ArgumentParser("score")
parser.add_argument("--model_input", type=str, help="Path of input model.")
parser.add_argument("--test_data", type=str, help="Path to test data.")
parser.add_argument("--score_output", type=str, help="Path of scoring output.")

args = parser.parse_args()

lines = [
    f"Model path: {args.model_input}",
    f"Test data path: {args.test_data}",
    f"Scoring output path: {args.score_output}",
]

for line in lines:
    print(line)

# Load the model from input port
# Here only print the model as text since it is a dummy one
model = (Path(args.model_input) / "model").read_text()
print("Model:", model)

# Do scoring with the input model
# Here only print text to output file as demo
(Path(args.score_output) / "score").write_text("scored with {}".format(model))

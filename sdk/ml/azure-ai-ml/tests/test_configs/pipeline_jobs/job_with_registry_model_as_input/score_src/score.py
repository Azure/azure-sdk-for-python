import argparse

parser = argparse.ArgumentParser("score")
parser.add_argument("--model_input", type=str, help="Path of input model")
parser.add_argument("--test_data", type=str, help="Path to test data")
parser.add_argument("--score_output", type=str, help="Path of scoring output")

args = parser.parse_args()

print("hello scoring world...")

lines = [
    f"Model path: {args.model_input}",
    f"Test data path: {args.test_data}",
    f"Scoring output path: {args.score_output}",
]

for line in lines:
    print(line)

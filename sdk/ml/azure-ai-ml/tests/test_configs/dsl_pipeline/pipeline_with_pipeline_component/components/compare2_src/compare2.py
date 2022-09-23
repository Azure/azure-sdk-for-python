import argparse
from pathlib import Path

parser = argparse.ArgumentParser("compare2")
parser.add_argument("--model1", type=str, help="The first model to compare with")
parser.add_argument("--eval_result1", type=str, help="The evaluation result of first model")
parser.add_argument("--model2", type=str, help="The second model to compare")
parser.add_argument("--eval_result2", type=str, help="The evaluation result of second model")
parser.add_argument("--best_model", type=str, help="The better model among the two")
parser.add_argument("--best_result", type=str, help="The better model evalution result among the two")


args = parser.parse_args()

lines = [
    f"Model #1: {args.model1}",
    f"Evaluation #1: {args.eval_result1}",
    f"Model #2: {args.model2}",
    f"Evaluation #2: {args.eval_result2}",
    f"Best model path: {args.best_model}",
]

Path(args.best_model).mkdir(parents=True, exist_ok=True)
model_output = Path(args.best_model) / Path("model").name
with open(model_output, "w") as file:
    for line in lines:
        print(line)
        file.write(line + "\n")

Path(args.best_result).mkdir(parents=True, exist_ok=True)
result_output = Path(args.best_result) / Path("result").name
with open(result_output, "w") as file:
    for line in lines:
        print(line)
        file.write(line + "\n")

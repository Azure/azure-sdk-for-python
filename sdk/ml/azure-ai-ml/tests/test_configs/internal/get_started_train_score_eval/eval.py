import argparse
from pathlib import Path

parser = argparse.ArgumentParser("eval")
parser.add_argument("--scoring_result", type=str, help="Path of scoring result.")
parser.add_argument("--eval_output", type=str, help="Path of output evaluation result.")

args = parser.parse_args()

lines = [
    f"Scoring result path: {args.scoring_result}",
    f"Evaluation output path: {args.eval_output}",
]

for line in lines:
    print(line)

# Evaluate the incoming scoring result and output evaluation result.
# Here only output a dummy file for demo.
(Path(args.eval_output) / "eval_result").write_text("eval_result")

import argparse
import pandas as pd
import os
from pathlib import Path
from sklearn.linear_model import LinearRegression
import pickle
from sklearn.metrics import mean_squared_error, r2_score

parser = argparse.ArgumentParser("score")
parser.add_argument("--predictions", type=str, help="Path of predictions and actual data")
parser.add_argument("--model", type=str, help="Path to model")
parser.add_argument("--score_report", type=str, help="Path to score report")


args = parser.parse_args()

print("hello scoring world...")

lines = [
    f"Model path: {args.model}",
    f"Predictions path: {args.predictions}",
    f"Scoring output path: {args.score_report}",
]

for line in lines:
    print(line)

# Load the test data with predicted values

print("mounted_path files: ")
arr = os.listdir(args.predictions)

print(arr)
df_list = []
for filename in arr:
    print("reading file: %s ..." % filename)
    with open(os.path.join(args.predictions, filename), "r") as handle:
        # print (handle.read())
        input_df = pd.read_csv((Path(args.predictions) / filename))
        df_list.append(input_df)

test_data = df_list[0]

# Load the model from input port
model = pickle.load(open((Path(args.model) / "model.sav"), "rb"))

# Print the results of scoring the predictions against actual values in the test data
# The coefficients
print("Coefficients: \n", model.coef_)

actuals = test_data["actual_cost"]
predictions = test_data["predicted_cost"]

# The mean squared error
print("Mean squared error: %.2f" % mean_squared_error(actuals, predictions))
# The coefficient of determination: 1 is perfect prediction
print("Coefficient of determination: %.2f" % r2_score(actuals, predictions))
print("Model: ", model)

# Print score report to a text file
(Path(args.score_report) / "score.txt").write_text("Scored with the following model:\n{}".format(model))
with open((Path(args.score_report) / "score.txt"), "a") as f:
    f.write("\n Coefficients: \n %s \n" % str(model.coef_))
    f.write("Mean squared error: %.2f \n" % mean_squared_error(actuals, predictions))
    f.write("Coefficient of determination: %.2f \n" % r2_score(actuals, predictions))

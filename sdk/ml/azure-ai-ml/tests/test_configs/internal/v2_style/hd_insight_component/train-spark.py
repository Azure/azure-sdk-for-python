import argparse
import os
import sys

import pyspark
from pyspark.ml.classification import *
from pyspark.ml.evaluation import *
from pyspark.ml.feature import *
from pyspark.sql.functions import *
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

# Get args
parser = argparse.ArgumentParser()
parser.add_argument("--input_path")
parser.add_argument("--regularization_rate")
parser.add_argument("--output_path")
args, _ = parser.parse_known_args()
input_path = args.input_path
regularization_rate = args.regularization_rate
output_path = args.output_path

print("input_path: {}".format(input_path))
print("regularization_rate: {}".format(regularization_rate))
print("output_path: {}".format(output_path))

# start Spark session
spark = pyspark.sql.SparkSession.builder.appName("Iris").getOrCreate()

# print runtime versions
print("****************")
print("Python version: {}".format(sys.version))
print("Spark version: {}".format(spark.version))
print("****************")

# load iris.csv into Spark dataframe
schema = StructType(
    [
        StructField("sepal-length", DoubleType()),
        StructField("sepal-width", DoubleType()),
        StructField("petal-length", DoubleType()),
        StructField("petal-width", DoubleType()),
        StructField("class", StringType()),
    ]
)

data = spark.read.csv(input_path, header=True, schema=schema)

print("First 10 rows of Iris dataset:")
data.show(10)

# vectorize all numerical columns into a single feature column
feature_cols = data.columns[:-1]
assembler = pyspark.ml.feature.VectorAssembler(inputCols=feature_cols, outputCol="features")
data = assembler.transform(data)

# convert text labels into indices
data = data.select(["features", "class"])
label_indexer = pyspark.ml.feature.StringIndexer(inputCol="class", outputCol="label").fit(data)
data = label_indexer.transform(data)

# only select the features and label column
data = data.select(["features", "label"])
print("Reading for machine learning")
data.show(10)

# use Logistic Regression to train on the training set
train, test = data.randomSplit([0.70, 0.30])
reg = float(regularization_rate)
lr = pyspark.ml.classification.LogisticRegression(regParam=reg)
model = lr.fit(train)

model.save(os.path.join(output_path, "iris.model"))

# predict on the test set
prediction = model.transform(test)
print("Prediction")
prediction.show(10)

# evaluate the accuracy of the model using the test set
evaluator = pyspark.ml.evaluation.MulticlassClassificationEvaluator(metricName="accuracy")
accuracy = evaluator.evaluate(prediction)

print()
print("#####################################")
print("Regularization rate is {}".format(reg))
print("Accuracy is {}".format(accuracy))
print("#####################################")
print()

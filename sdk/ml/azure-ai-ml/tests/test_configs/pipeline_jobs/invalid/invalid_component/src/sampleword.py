import argparse

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# read command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input1")
parser.add_argument("--output2")
parser.add_argument("--my_sample_rate", type=float)
args = parser.parse_args()


df = spark.read.text(args.input1)

# sample df with my_sample_rate
sampled_df = df.sample(args.my_sample_rate)
sampled_df.write.text(args.output2)

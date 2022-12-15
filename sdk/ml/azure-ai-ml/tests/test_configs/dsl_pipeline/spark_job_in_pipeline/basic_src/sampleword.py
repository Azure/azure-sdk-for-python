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

# sampled_df = sampled_df.toPandas()
# sampled_df.to_csv("args.output2", sep="\t", index=False)
# sampled_df.repartition(1).write.text(args.output2)

# sc = spark.sparkContext
# textRDD1 = sc.textFile(args.input1)
# sampled_df = textRDD1.sample(False, args.my_sample_rate, 1)
# sampled_df.saveAsTextFile(args.output2)

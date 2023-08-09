import argparse
from operator import add

# from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

parser = argparse.ArgumentParser()
parser.add_argument("--input1")
args = parser.parse_args()

spark = SparkSession.builder.appName("PythonWordCount").getOrCreate()

lines = spark.read.text(args.input1).rdd.map(lambda r: r[0])
counts = lines.flatMap(lambda x: x.split(" ")).map(lambda x: (x, 1)).reduceByKey(add)
output = counts.collect()
for word, count in output:
    print("%s: %i" % (word, count))

import argparse

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
sc = spark.sparkContext

parser = argparse.ArgumentParser()
parser.add_argument("--file_input")
parser.add_argument("--output")
args = parser.parse_args()

arr = sc._gateway.new_array(sc._jvm.java.lang.String, 2)
arr[0] = args.file_input
arr[1] = args.output
obj = sc._jvm.WordCount
obj.main(arr)

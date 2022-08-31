from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
import argparse

from utils import util

spark = SparkSession.builder.getOrCreate()
sc = spark.sparkContext

parser = argparse.ArgumentParser()
parser.add_argument("--file_input1")
parser.add_argument("--file_input2")
parser.add_argument("--output")
args = parser.parse_args()

greeting_udf = udf(util.greeting)
df = spark.read.option("header", "true").csv(args.file_input1)

df = df.withColumn("greeting", greeting_udf(df.species)).show()

print(sc.getConf().getAll())
arr = sc._gateway.new_array(sc._jvm.java.lang.String, 2)
arr[0] = args.file_input2
arr[1] = args.output
obj = sc._jvm.WordCount
obj.main(arr)

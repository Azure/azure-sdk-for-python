import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from utils import util

spark = SparkSession.builder.getOrCreate()
sc = spark.sparkContext

parser = argparse.ArgumentParser()
parser.add_argument("--file_input")
args = parser.parse_args()

greeting_udf = udf(util.greeting)
df = spark.read.option("header", "true").csv(args.file_input)

df = df.withColumn("greeting", greeting_udf(df.species)).show()

print(sc.getConf().getAll())

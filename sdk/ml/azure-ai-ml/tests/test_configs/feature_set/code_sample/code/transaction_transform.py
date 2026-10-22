from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.ml import Transformer
from pyspark.sql.dataframe import DataFrame


class TransactionFeatureTransformer(Transformer):
    def _transform(self, df: DataFrame) -> DataFrame:
        def days(i):
            return i * 86400

        w_3d = Window.partitionBy("accountID").orderBy(F.col("timestamp").cast("long")).rangeBetween(-days(3), 0)
        w_7d = Window.partitionBy("accountID").orderBy(F.col("timestamp").cast("long")).rangeBetween(-days(7), 0)
        res = (
            df.withColumn("transaction_7d_count", F.count("transactionID").over(w_7d))
            .withColumn("transaction_amount_7d_sum", F.sum("transactionAmount").over(w_7d))
            .withColumn("transaction_amount_7d_avg", F.avg("transactionAmount").over(w_7d))
            .withColumn("transaction_3d_count", F.count("transactionID").over(w_3d))
            .withColumn("transaction_amount_3d_sum", F.sum("transactionAmount").over(w_3d))
            .withColumn("transaction_amount_3d_avg", F.avg("transactionAmount").over(w_3d))
            .select(
                "accountID",
                "timestamp",
                "transaction_3d_count",
                "transaction_amount_3d_sum",
                "transaction_amount_3d_avg",
                "transaction_7d_count",
                "transaction_amount_7d_sum",
                "transaction_amount_7d_avg",
            )
        )
        return res

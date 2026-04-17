import math
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, FloatType, ArrayType
from utils import parse_opening_hours, get_lat, get_lon, h3_res_9, h3_res_8, h3_res_7
from fetch_score import score_tag

lat = udf(get_lat, StringType())
lon = udf(get_lon, StringType())
h3_cell_9 = udf(h3_res_9, StringType())
h3_cell_8 = udf(h3_res_8, StringType())
h3_cell_7 = udf(h3_res_7, StringType())
fetch_hours = udf(parse_opening_hours, StringType())
score = udf(score_tag, StringType())

spark = SparkSession.builder.appName('osm_pipeline').getOrCreate()

df = spark.read.parquet('/spark/files/*/')

df = df.filter(df.amenity.isNotNull() | df.shop.isNotNull() | df.leisure.isNotNull()) \
    .withColumn("lat", lat("coordinates")) \
    .withColumn("lon", lon("coordinates")) \
    .withColumn("h3_res_9", h3_cell_9(F.col('lat'), F.col('lon'))) \
    .withColumn("h3_res_8", h3_cell_8(F.col('lat'), F.col('lon'))) \
    .withColumn("h3_res_7", h3_cell_7(F.col('lat'), F.col('lon'))) \
    .withColumn('amenity_score', score(F.col('amenity'))) \
    .withColumn('typical_intervals', fetch_hours(F.col('opening_hours'))) \
    .drop("opening_hours", "coordinates")

ideal_records_per_file = 2000000 
total_count = df.count()
n_partitions = math.ceil(total_count / ideal_records_per_file)

df.coalesce(n_partitions).write.parquet('/spark/transformed/', mode = 'overwrite')

spark.stop()

print("SUCCESS \\o/")
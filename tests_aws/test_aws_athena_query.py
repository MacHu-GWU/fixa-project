# -*- coding: utf-8 -*-

import textwrap
import polars as pl
from boto_session_manager import BotoSesManager
from s3pathlib import S3Path
from fixa.aws.aws_athena_query import read_athena_query_result, run_athena_query

bsm = BotoSesManager(profile_name="awshsh_app_dev_us_east_1")
# bsm = BotoSesManager(region_name="us-east-1")
s3bucket = S3Path(f"{bsm.aws_account_id}-{bsm.aws_region}-data")
s3dir_athena_result = s3bucket.joinpath("athena", "results").to_dir()

database = "dynamodb_to_datalake"

sql = textwrap.dedent(f"""
SELECT * 
FROM transactions 
LIMIT 10; 
""")

lazy_df, exec_id = run_athena_query(
    bsm=bsm,
    s3dir_result=s3dir_athena_result,
    sql=sql,
    database=database,
    result_cache_expire=60,
)
print(exec_id)

# exec_id = "cad5bc4a-db1e-469d-b8a8-d600eb23833a"
# lazy_df = read_athena_query_result(
#     bsm=bsm,
#     s3dir_result=s3dir_athena_result,
#     exec_id=exec_id,
#     verbose=True,
# )

with pl.Config() as cfg:
    cfg.set_tbl_cols(-1)
    cfg.set_tbl_width_chars(1000)
    df = lazy_df.collect()
    print(df)

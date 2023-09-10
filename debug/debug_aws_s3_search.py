# -*- coding: utf-8 -*-

from pathlib import Path

import sqlalchemy as sa
from sqlalchemy import orm
from s3pathlib import S3Path
from boto_session_manager import BotoSesManager
from rich import print as rprint

from fixa.aws.aws_s3_search import create_sqlite_engine, S3Object, S3Database


p = Path(__file__).absolute().parent.joinpath("debug_aws_s3_search.sqlite")
p.unlink(missing_ok=True)
engine = create_sqlite_engine(path=str(p))
db = S3Database(engine=engine)

bsm = BotoSesManager(profile_name="awshsh_app_dev_us_east_1", region_name="us-east-1")
bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-data"
s3bucket = S3Path(bucket)
s3dir_projects = s3bucket.joinpath("athena").to_dir()

# db.load_s3dir(s3dir_projects.uri, bsm.s3_client, limit=1000)
# db.load_s3dir(s3dir_projects.uri, bsm.s3_client, ignore_metadata=True, ignore_tags=True, expire=900)

# for dct in db.s3object_list(return_entity=False):
#     rprint(dict(dct))

# for dct in db.loaded_s3dir_list(return_entity=False):
#     rprint(dict(dct))

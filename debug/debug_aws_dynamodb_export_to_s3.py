# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from fixa.aws.aws_dynamodb_export_to_s3 import Export
from fixa.timer import DateTimeTimer
from rich import print as rprint

bsm = BotoSesManager(profile_name="awshsh_app_dev_us_east_1")
bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-data"
table_arn = f"arn:aws:dynamodb:{bsm.aws_region}:{bsm.aws_account_id}:table/transaction"

# export = Export.export_table_to_point_in_time(dynamodb_client=bsm.dynamodb_client, table_arn=table_arn, s3_bucket=bucket, s3_prefix="projects/dynamodb_to_datalake/dynamodb_export/")
# rprint(export)
#
# export = Export.describe_export(
#     bsm.dynamodb_client,
#     export_arn=f"arn:aws:dynamodb:{bsm.aws_region}:{bsm.aws_account_id}:table/transaction/export/01690752899887-0a3d5969",
# )
# rprint(export)
#
# manifest_summary = export.get_manifest_summary(bsm.dynamodb_client, bsm.s3_client)
# rprint(manifest_summary)
#
# data_files = export.get_data_files(bsm.dynamodb_client, bsm.s3_client)
# rprint(data_files)
#
# for data_file in data_files:
#     rows = data_file.read_items(bsm.s3_client)
#     rprint(rows)
#
# items = list(export.read_items(bsm.dynamodb_client, bsm.s3_client))
# for item in export.read_items(bsm.dynamodb_client, bsm.s3_client):
#     rprint(item)
#
# export_list = Export.list_exports(
#     bsm.dynamodb_client,
#     table_arn=table_arn,
#     get_details=True,
# )
# rprint(export_list)

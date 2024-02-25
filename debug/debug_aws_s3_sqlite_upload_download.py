# -*- coding: utf-8 -*-

"""
这是利用 AWS S3 Lock 实现的一个 App. 它能将不支持网络连接的 sqlite 数据库当成网络数据库用.
其原理是每次运行一个 Job 之前, 都先从 S3 将 sqlite 文件下载下来, 同时用 Lock 锁住, 防止
其他 Job 同时运行. 运行完毕后, 再将 sqlite 文件上传到 S3, 并释放 Lock. 这样就能保证同一时间
只有一个 Job 在使用 sqlite.
"""

from pathlib_mate import Path
from boto_session_manager import BotoSesManager
from s3pathlib import S3Path, context
from fixa.aws.aws_s3_lock import AlreadyLockedError, Lock, Vault

# configure the boto3 session
bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
context.attach_boto_session(bsm.boto_ses)

# configure sqlite file S3 location
s3dir = S3Path(
    "s3://bmt-app-dev-us-east-1-data/projects/aws_s3_sqlite_upload_download/"
).to_dir()
s3path = s3dir / "test.txt"

# configure local sqlite file location
path = Path.dir_here(__file__) / "test.txt"

# configure S3 lock vault location
vault = Vault(
    bucket=s3path.bucket,
    key=s3path.key,
    expire=900,  # how long we automatically release a dead lock
    wait=1.0,  # the higher the value, the more reliable of this mechanism but we need to wait longer before doing any task
)


# acquire the lock before doing any task
def main():
    lock = vault.acquire(bsm.s3_client, owner="alice")
    if s3path.exists():
        bsm.s3_client.download_file(
            Bucket=s3path.bucket, Key=s3path.key, Filename=str(path)
        )

    # do something with the sqlite database
    pass
    # acquire lock before uploading, this action also update the lock expiration time
    lock = vault.acquire(bsm.s3_client, owner="alice")
    s3path.upload_file(path)

    # do something with the sqlite database
    pass
    # acquire lock before uploading, this action also update the lock expiration time
    lock = vault.acquire(bsm.s3_client, owner="alice")
    s3path.upload_file(path)

    # at the end of the job, release the lock
    vault.release(bsm.s3_client, lock)


if __name__ == "__main__":
    main()

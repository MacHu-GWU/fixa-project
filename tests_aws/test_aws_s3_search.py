# -*- coding: utf-8 -*-

import time

import moto

from s3pathlib import S3Path, context
import sqlalchemy as sa
from sqlalchemy import orm

from fixa.aws.mock_test import BaseMockTest
from fixa.aws.aws_s3_search import create_sqlite_engine, S3Object, S3Database


class Test(BaseMockTest):
    mock_list = [
        moto.mock_s3,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        # set default boto session
        context.attach_boto_session(cls.bsm.boto_ses)

        # create bucket
        cls.bucket = "my-bucket"
        cls.bsm.s3_client.create_bucket(Bucket=cls.bucket)
        s3bucket = S3Path(cls.bucket)
        cls.s3bucket = s3bucket

        # insert file
        s3bucket.joinpath("file.txt").write_text(
            "hello alice",
            content_type="text/plain",
            metadata={"mk1": "mv1"},
        )
        s3bucket.joinpath("folder", "data.json").write_text(
            '{"name": "alice", "email": "alice@example.com"}',
            content_type="application/json",
            tags={"tk1": "tv1"},
        )

        # reset database
        cls.engine = create_sqlite_engine()
        cls.db = S3Database(engine=cls.engine)

    def _test(self):
        assert len(self.db.loaded_s3dir_list()) == 0
        assert len(self.db.s3object_list()) == 0

        self.db.load_s3dir(self.s3bucket.uri, self.bsm.s3_client, expire=1)
        loaded_s3dir_1 = self.db.loaded_s3dir_list(return_entity=True)[0]
        assert loaded_s3dir_1.n_object == 2
        assert loaded_s3dir_1.expire == 1

        self.db.load_many_s3dir([self.s3bucket.uri], self.bsm.s3_client, expire=1)
        loaded_s3dir_2 = self.db.loaded_s3dir_list(return_entity=True)[0]
        assert loaded_s3dir_1.n_object == 2
        assert loaded_s3dir_1.expire == 1
        assert loaded_s3dir_1.start_time == loaded_s3dir_2.start_time
        assert loaded_s3dir_1.end_time == loaded_s3dir_2.end_time

        time.sleep(1.5)
        self.db.load_many_s3dir([self.s3bucket.uri], [self.bsm.s3_client], expire=3)
        loaded_s3dir_3 = self.db.loaded_s3dir_list(return_entity=True)[0]
        assert loaded_s3dir_3.n_object == 2
        assert loaded_s3dir_3.expire == 3
        assert loaded_s3dir_1.start_time != loaded_s3dir_3.start_time
        assert loaded_s3dir_1.end_time != loaded_s3dir_3.end_time

        # select all, return S3Object
        stmt = sa.select(S3Object).where(S3Object.bucket == self.bucket)

        with orm.Session(self.db.engine) as ses:
            obj: S3Object
            for obj in ses.scalars(stmt):
                _ = obj.uri
                # print(obj.uri)

        # select all, return dict-like RowMapping
        with self.engine.connect() as conn:
            for dct in conn.execute(stmt).mappings():
                _ = dct["uri"]
                # print(dct)

        # filter by file size
        stmt = sa.select(S3Object).where(
            S3Object.size >= 20,
        )
        for obj in self.db.query(stmt, return_entity=True):
            assert obj.size >= 20

        # filter by file extension
        stmt = sa.select(S3Object).where(
            S3Object.ext == ".txt",
        )
        for dct in self.db.query(stmt, return_entity=False):
            assert dct["ext"] == ".txt"

        # filter by prefix
        stmt = sa.select(S3Object).where(
            S3Object.key.startswith("folder"),
        )
        for obj in self.db.query(stmt, return_entity=True):
            assert obj.key.startswith("folder")

        # filter by metadata or tag, return S3Object
        stmt = sa.select(S3Object).where(
            S3Object.meta["mk1"].as_string() == "mv1",
        )

        with orm.Session(self.db.engine) as ses:
            for obj in ses.scalars(stmt):
                assert obj.meta == {"mk1": "mv1"}

        # filter by metadata or tag, return dict-like RowMapping
        with self.engine.connect() as conn:
            for dct in conn.execute(stmt).mappings():
                assert dct["meta"] == {"mk1": "mv1"}

        # clear db
        assert len(self.db.s3object_list()) == 2
        assert len(self.db.loaded_s3dir_list()) == 1

        self.db.clear()
        assert len(self.db.loaded_s3dir_list(return_entity=True)) == 0
        assert len(self.db.s3object_list(return_entity=True)) == 0

        self.db.clear_s3dir(self.s3bucket.uri)
        assert len(self.db.loaded_s3dir_list(return_entity=True)) == 0
        assert len(self.db.s3object_list(return_entity=True)) == 0

    def test(self):
        print("")
        self._test()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.aws_s3_search", preview=False)

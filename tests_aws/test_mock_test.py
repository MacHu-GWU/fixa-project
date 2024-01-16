# -*- coding: utf-8 -*-

"""
.. note::

    We need to ensure that the mock start and mock stop are working as expected
    when we have multiple subclass.
"""

import moto
from fixa.aws.mock_test import (
    BaseMockTest,
)


class TestS3(BaseMockTest):
    mock_list = [
        moto.mock_s3,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm.s3_client.create_bucket(Bucket="my-bucket")
        cls.bsm.s3_client.put_object(
            Bucket="my-bucket",
            Key="file.txt",
            Body="hello world",
        )

    def test(self):
        assert (
            self.bsm.s3_client.get_object(Bucket="my-bucket", Key="file.txt")["Body"]
            .read()
            .decode("utf-8")
            == "hello world"
        )


class TestIam(BaseMockTest):
    mock_list = [
        moto.mock_iam,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bsm.iam_client.create_group(GroupName="Admin")

    def test(self):
        assert (
            self.bsm.iam_client.get_group(GroupName="Admin")["Group"]["GroupName"]
            == "Admin"
        )


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.mock_test", preview=False)

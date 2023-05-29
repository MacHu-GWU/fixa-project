# -*- coding: utf-8 -*-

import moto
from fixa.aws.mock_test import (
    BaseMockTest,
)


class Test(BaseMockTest):
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


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.mock_test", preview=False)

# -*- coding: utf-8 -*-

import json
import dataclasses

import moto

from fixa.aws.mock_test import BaseMockTest
from fixa.aws.aws_s3_tracker import BaseTracker, Backend


@dataclasses.dataclass
class Tracker(BaseTracker):
    offset: int = dataclasses.field()

    @classmethod
    def default(cls):
        return cls(offset=0)

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def from_json(cls, json_str: str):
        return cls(**json.loads(json_str))

    def awesome_method(self):
        pass


class Test(BaseMockTest):
    mock_list = [
        moto.mock_s3,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bucket = "my-bucket"
        cls.bsm.s3_client.create_bucket(Bucket=cls.bucket)

    def _test(self):
        backend = Backend(bucket=self.bucket, key="tracker.json", tracker_class=Tracker)

        tracker = backend.read(self.bsm.s3_client)
        assert tracker.offset == 0
        tracker.awesome_method()

        tracker.offset = 1
        backend.write(self.bsm.s3_client, tracker)

        tracker = backend.read(self.bsm.s3_client)
        assert tracker.offset == 1
        tracker.awesome_method()

    def test(self):
        print("")
        self._test()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.aws_s3_tracker", preview=False)

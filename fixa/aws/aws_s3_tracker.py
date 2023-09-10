# -*- coding: utf-8 -*-

"""
A simple tracker that can be used to track the progress of a long process.
For example, you are trying to download data from 2000-01-01 to 2020-01-01,
and you split them into 20 years chunks, and you download them one by one.
You can use tracker to track the last succeeded year.

I suggest to use this module with :mod:`fixa.aws.aws_s3_lock` module, so
you can have a distributive lock to prevent multiple processes to update the tracker.

Requirements::

    python>=3.7
    boto3

Usage:

.. code-block:: python

    import dataclasses
    from aws_s3_tracker import BaseTracker, Backend

    # BaseTracker is a dataclasses, you have to use dataclasses.dataclass decorator here
    @dataclasses.dataclass
    class Tracker(BaseTracker):
        year: int = dataclasses.field()

        @classmethod
        def default(cls):
            return cls(year=2000)

        def to_json(self) -> str:
            return json.dumps(dataclasses.asdict(self))

        @classmethod
        def from_json(cls, json_str: str):
            return cls(**json.loads(json_str))

    backend = Backend(bucket="my-bucket", key="tracker.json", tracker_class=Tracker)

    # read tracker, if the tracker does not exist, it will create a default one
    tracker = backend.read(s3_client)
    assert tracker.year == 2000

    # update tracker and write it back to S3
    tracker.year = 2001
    backend.write(s3_client, tracker)

    # read tracker again, you will get the updated one
    tracker = backend.read(s3_client)
    assert tracker.year == 2001
"""


import typing as T
import dataclasses

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


@dataclasses.dataclass
class BaseTracker:
    """
    The base tracker class. It is a dataclasses, you have to put @dataclasses.dataclass
    decorator on your own tracker class.

    It has to implement three methods:

    - ``default``: a constructor class method that create a default tracker.
    - ``to_json``: serialize the tracker to a json string.
    - ``from_json``: deserialize the tracker from a json string.
    """

    @classmethod
    def default(cls):
        raise NotImplementedError

    def to_json(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_str: str):
        raise NotImplementedError


@dataclasses.dataclass
class Backend:
    """
    A backend is an S3 object to store a lock.

    :param bucket: the S3 bucket.
    :param key: the S3 key.
    :param tracker_class: the user tracker class.
    """

    bucket: str = dataclasses.field()
    key: str = dataclasses.field()
    tracker_class: T.Any = dataclasses.field()

    def read(self, s3_client: "S3Client"):
        """
        Read the tracker from S3.
        """
        try:
            response = s3_client.get_object(Bucket=self.bucket, Key=self.key)
            return self.tracker_class.from_json(response["Body"].read().decode("utf-8"))
        except Exception as e:
            if "NoSuchKey" in str(e):
                tracker = self.tracker_class.default()
                self.write(s3_client=s3_client, tracker=tracker)
                return tracker
            else:  # pragma: no cover
                raise e

    def write(self, s3_client: "S3Client", tracker):
        """
        Write the tracker to S3.
        """
        s3_client.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=tracker.to_json(),
            ContentType="application/json",
        )

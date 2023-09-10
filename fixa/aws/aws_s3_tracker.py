# -*- coding: utf-8 -*-

import typing as T
import json
import time
import uuid
import dataclasses
from datetime import datetime, timezone


@dataclasses.dataclass
class BaseTracker:
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
    """

    bucket: str = dataclasses.field()
    key: str = dataclasses.field()

    def read(self, s3_client, tracker_class):
        try:
            response = s3_client.get_object(Bucket=self.bucket, Key=self.key)
            return tracker_class.from_json(response["Body"].read().decode("utf-8"))
        except Exception as e:
            if "NoSuchKey" in str(e):
                tracker = tracker_class.default()
                self.write(s3_client=s3_client, tracker=tracker)
                return tracker
            else:  # pragma: no cover
                raise e

    def write(self, s3_client, tracker):
        s3_client.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=tracker.to_json(),
            ContentType="application/json",
        )

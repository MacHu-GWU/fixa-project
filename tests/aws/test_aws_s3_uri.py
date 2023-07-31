# -*- coding: utf-8 -*-

import pytest
from fixa.aws import aws_s3_uri


def test_split_s3_uri():
    s3_uri = "s3://my-bucket/my-prefix/my-file.zip"
    bucket, key = aws_s3_uri.split_s3_uri(s3_uri)
    assert bucket == "my-bucket"
    assert key == "my-prefix/my-file.zip"


def test_join_s3_uri():
    bucket = "my-bucket"
    key = "my-prefix/my-file.zip"
    s3_uri = aws_s3_uri.join_s3_uri(bucket, key)
    assert s3_uri == "s3://my-bucket/my-prefix/my-file.zip"


def test_split_parts():
    assert aws_s3_uri.split_parts("a/b/c") == ["a", "b", "c"]
    assert aws_s3_uri.split_parts("//a//b//c//") == ["a", "b", "c"]
    assert aws_s3_uri.split_parts("") == []
    assert aws_s3_uri.split_parts("////") == []


def test_s3_key_smart_join():
    assert aws_s3_uri.smart_join_s3_key(
        parts=["/a/", "b/", "/c"],
        is_dir=True,
    ) == "a/b/c/"

    assert aws_s3_uri.smart_join_s3_key(
        parts=["/a/", "b/", "/c"],
        is_dir=False,
    ) == "a/b/c"

    assert aws_s3_uri.smart_join_s3_key(
        parts=["//a//b//c//"],
        is_dir=True,
    ) == "a/b/c/"

    assert aws_s3_uri.smart_join_s3_key(
        parts=["//a//b//c//"],
        is_dir=False,
    ) == "a/b/c"


def test_make_s3_console_url():
    # object
    url = aws_s3_uri.make_s3_console_url("my-bucket", "my-file.zip")
    assert "object" in url

    # folder
    url = aws_s3_uri.make_s3_console_url("my-bucket", "my-folder/")
    assert "bucket" in url

    # uri
    url = aws_s3_uri.make_s3_console_url(s3_uri="s3://my-bucket/my-folder/data.json")
    assert url == "https://console.aws.amazon.com/s3/object/my-bucket?prefix=my-folder/data.json"

    # s3 bucket root
    url = aws_s3_uri.make_s3_console_url(s3_uri="s3://my-bucket/")
    assert url == "https://console.aws.amazon.com/s3/buckets/my-bucket?tab=objects"

    # version id
    url = aws_s3_uri.make_s3_console_url(s3_uri="s3://my-bucket/my-folder/my-file.zip", version_id="v123")
    assert url == "https://console.aws.amazon.com/s3/object/my-bucket?prefix=my-folder/my-file.zip&versionId=v123"

    # us gov cloud
    url = aws_s3_uri.make_s3_console_url(
        s3_uri="s3://my-bucket/my-folder/data.json", is_us_gov_cloud=True
    )
    assert url == "https://console.amazonaws-us-gov.com/s3/object/my-bucket?prefix=my-folder/data.json"

    with pytest.raises(ValueError):
        aws_s3_uri.make_s3_console_url(bucket="")

    with pytest.raises(ValueError):
        aws_s3_uri.make_s3_console_url(prefix="", s3_uri="")


def test_ensure_s3_object():
    aws_s3_uri.ensure_s3_object("path/to/key")
    with pytest.raises(Exception):
        aws_s3_uri.ensure_s3_object("path/to/dir/")


def test_ensure_s3_dir():
    aws_s3_uri.ensure_s3_dir("path/to/dir/")
    with pytest.raises(Exception):
        aws_s3_uri.ensure_s3_dir("path/to/key")


if __name__ == "__main__":
    from fixa.tests import run_cov_test
    
    run_cov_test(__file__, "fixa.aws.aws_s3_uri", preview=False)

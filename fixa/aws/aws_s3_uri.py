# -*- coding: utf-8 -*-

import typing as T


def split_s3_uri(
    s3_uri: str,
) -> T.Tuple[str, str]:
    """
    Split AWS S3 URI, returns bucket and key.

    :param s3_uri: example, ``"s3://my-bucket/my-folder/data.json"``
    """
    parts = s3_uri.split("/")
    bucket = parts[2]
    key = "/".join(parts[3:])
    return bucket, key


def join_s3_uri(
    bucket: str,
    key: str,
) -> str:
    """
    Join AWS S3 URI from bucket and key.

    :param bucket: example, ``"my-bucket"``
    :param key: example, ``"my-folder/data.json"`` or ``"my-folder/"``

    .. versionadded:: 1.0.1
    """
    return "s3://{}/{}".format(bucket, key)


def split_parts(key: str) -> T.List[str]:
    """
    Split s3 key parts using "/" delimiter.

    Example::

        >>> split_parts("a/b/c")
        ["a", "b", "c"]
        >>> split_parts("//a//b//c//")
        ["a", "b", "c"]

    .. versionadded:: 1.0.1
    """
    return [part for part in key.split("/") if part]


def smart_join_s3_key(
    parts: T.List[str],
    is_dir: bool,
) -> str:
    """
    Note, it assume that there's no such double slack in your path. It ensure
    that there's only one consecutive "/" in the s3 key.

    :param parts: list of s3 key path parts, could have "/"
    :param is_dir: if True, the s3 key ends with "/". otherwise enforce no
        tailing "/".

    Example::

        >>> smart_join_s3_key(parts=["/a/", "b/", "/c"], is_dir=True)
        a/b/c/
        >>> smart_join_s3_key(parts=["/a/", "b/", "/c"], is_dir=False)
        a/b/c
    """
    new_parts = list()
    for part in parts:
        new_parts.extend(split_parts(part))
    key = "/".join(new_parts)
    if is_dir:
        return key + "/"
    else:
        return key


def make_s3_console_url(
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = None,
    s3_uri: T.Optional[str] = None,
    version_id: T.Optional[str] = None,
    is_us_gov_cloud: bool = False,
) -> str:
    """
    Return an AWS Console url that you can use to open it in your browser.

    :param bucket: example, ``"my-bucket"``
    :param prefix: example, ``"my-folder/"``
    :param s3_uri: example, ``"s3://my-bucket/my-folder/data.json"``

    Example::

        >>> make_s3_console_url(s3_uri="s3://my-bucket/my-folder/data.json")
        https://s3.console.aws.amazon.com/s3/object/my-bucket?prefix=my-folder/data.json
    """
    if s3_uri is None:
        if not ((bucket is not None) and (prefix is not None)):
            raise ValueError
    else:
        if not ((bucket is None) and (prefix is None)):
            raise ValueError
        bucket, prefix = split_s3_uri(s3_uri)

    if len(prefix) == 0:
        return "https://console.aws.amazon.com/s3/buckets/{}?tab=objects".format(
            bucket,
        )
    elif prefix.endswith("/"):
        s3_type = "buckets"
        prefix_part = f"prefix={prefix}"
    else:
        s3_type = "object"
        prefix_part = f"prefix={prefix}"

    if is_us_gov_cloud:
        endpoint = "console.amazonaws-us-gov.com"
    else:
        endpoint = "console.aws.amazon.com"

    if version_id is None:
        version_part = ""
    else:
        version_part = f"&versionId={version_id}"

    return f"https://{endpoint}/s3/{s3_type}/{bucket}?{prefix_part}{version_part}"


def make_s3_select_console_url(
    bucket: str,
    key: str,
    is_us_gov_cloud: bool,
) -> str:  # pragma: no cover
    if is_us_gov_cloud:
        endpoint = "console.amazonaws-us-gov.com"
    else:
        endpoint = "console.aws.amazon.com"
    return "https://{endpoint}/s3/buckets/{bucket}/object/select?prefix={key}".format(
        endpoint=endpoint,
        bucket=bucket,
        key=key,
    )


def ensure_s3_object(
    s3_key_or_uri: str,
) -> None:
    """
    Raise exception if the string is not in valid format for an AWS S3 object
    """
    if s3_key_or_uri.endswith("/"):
        raise ValueError("'{}' doesn't represent s3 object!".format(s3_key_or_uri))


def ensure_s3_dir(s3_key_or_uri: str) -> None:
    """
    Raise exception if the string is not in valid format for an AWS S3 directory
    """
    if not s3_key_or_uri.endswith("/"):
        raise ValueError("'{}' doesn't represent s3 dir!".format(s3_key_or_uri))

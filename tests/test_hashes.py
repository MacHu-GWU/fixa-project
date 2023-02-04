# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
from fixa.hashes import hashes, HashAlgoEnum


def test_settings():
    (
        hashes.use_md5()
        .use_sha1()
        .use_sha224()
        .use_sha256()
        .use_sha384()
        .use_sha512()
        .use_hexdigesst()
        .use_bytesdigest()
    )


def test_hash_file():
    hashes.use_sha256().use_hexdigesst()

    a_file = str(Path(__file__).absolute().parent.joinpath("all.py"))

    id1 = hashes.of_file(a_file)
    id2 = hashes.of_file(a_file, nbytes=1000)
    id3 = hashes.of_file(a_file, chunk_size=1)
    id4 = hashes.of_file(a_file, chunk_size=2)

    assert id1 == id2 == id3 == id4

    id1 = hashes.of_file(a_file, nbytes=5)
    id2 = hashes.of_file(a_file, nbytes=5, chunk_size=1)
    id3 = hashes.of_file(a_file, nbytes=5, chunk_size=2)
    assert id1 == id2 == id3

    with pytest.raises(ValueError):
        hashes.of_file(a_file, nbytes=-1)

    with pytest.raises(ValueError):
        hashes.of_file(a_file, chunk_size=0)


def test_hash_anything():
    """
    This test may failed in different operation system.
    """
    hashes.use_sha256().use_hexdigesst()

    a_bytes = b"hello world"

    assert isinstance(hashes.of_bytes(a_bytes), str)
    assert isinstance(hashes.of_bytes(a_bytes, hexdigest=False), bytes)

    hashes.use_bytesdigest()
    assert isinstance(hashes.of_bytes(a_bytes), bytes)
    assert isinstance(hashes.of_bytes(a_bytes, hexdigest=True), str)

    hashes.use_hexdigesst().use_md5()
    res1 = hashes.of_bytes(a_bytes)
    hashes.use_hexdigesst().use_sha256()
    res2 = hashes.of_bytes(a_bytes)
    res3 = hashes.of_bytes(a_bytes, algo=HashAlgoEnum.sha512)
    assert len({res1, res2, res3}) == 3

    a_str = "The God Father"
    hashes.of_str(a_str)

    assert hashes.of_bytes(a_bytes) == hashes.of_str_or_bytes(a_bytes)
    assert hashes.of_str(a_str) == hashes.of_str_or_bytes(a_str)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])

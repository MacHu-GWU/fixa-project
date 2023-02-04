# -*- coding: utf-8 -*-

"""
This module is built on Python standard hashlib, provides utility method
to find hash value for a bytes, a string, a Python object or a file.

Import this module::

    >>> from sfm.fingerprint import fingerprint

Example::

    >>> fingerprint.of_bytes(bytes(16))
    >>> fingerprint.of_text("Hello World")
    >>> fingerprint.of_pyobj(dict(a=1, b=2, c=3))
    >>> fingerprint.of_file("fingerprint.py")

You can switch the hash algorithm to use::

    >>> fingerprint.use("md5") # also "sha1", "sha256", "sha512"

Ref:

- hashlib: https://docs.python.org/3/library/hashlib.html
"""

import typing as T
import enum
import hashlib


class HashAlgoEnum(str, enum.Enum):
    md5 = "md5"
    sha1 = "sha1"
    sha224 = "sha224"
    sha256 = "sha256"
    sha384 = "sha384"
    sha512 = "sha512"


class Hashes:
    """
    A hashlib wrapper class allow you to use one line to do hash as you wish.

    :type algorithm: str
    :param algorithm: default "md5"

    Usage::

        >>> from sfm.fingerprint import fingerprint
        >>> print(fingerprint.of_bytes(bytes(123)))
        b1fec41621e338896e2d26f232a6b006

        >>> print(fingerprint.of_text("message"))
        78e731027d8fd50ed642340b7c9a63b3

        >>> print(fingerprint.of_pyobj({"key": "value"}))
        4c502ab399c89c8758a2d8c37be98f69

        >>> print(fingerprint.of_file("fingerprint.py"))
        4cddcb5562cbff652b0e4c8a0300337a
    """

    def __init__(
        self,
        algo: HashAlgoEnum = HashAlgoEnum.sha256,
        hexdigest: bool = True,
    ):
        self.algo = getattr(hashlib, algo.value)
        self.hexdigest: bool = hexdigest

    def use_md5(self) -> "Hashes":
        """
        Use md5 hash algorithm.
        """
        self.algo = getattr(hashlib, HashAlgoEnum.md5.value)
        return self

    def use_sha1(self) -> "Hashes":
        """
        Use sha1 hash algorithm.
        """
        self.algo = getattr(hashlib, HashAlgoEnum.sha1.value)
        return self

    def use_sha224(self) -> "Hashes":
        """
        Use sha224 hash algorithm.
        """
        self.algo = getattr(hashlib, HashAlgoEnum.sha224.value)
        return self

    def use_sha256(self) -> "Hashes":
        """
        Use sha256 hash algorithm.
        """
        self.algo = getattr(hashlib, HashAlgoEnum.sha256.value)
        return self

    def use_sha384(self) -> "Hashes":
        """
        Use sha384 hash algorithm.
        """
        self.algo = getattr(hashlib, HashAlgoEnum.sha384.value)
        return self

    def use_sha512(self) -> "Hashes":
        """
        Use sha512 hash algorithm.
        """
        self.algo = getattr(hashlib, HashAlgoEnum.sha512.value)
        return self

    def use_hexdigesst(self) -> "Hashes":
        """
        Return hash in hex string.
        """
        self.hexdigest = True
        return self

    def use_bytesdigest(self) -> "Hashes":
        """
        Return hash in bytes.
        """
        self.hexdigest = False
        return self

    def _construct(self, algo: T.Optional[HashAlgoEnum] = None):
        if algo is None:
            return self.algo()
        else:
            return getattr(hashlib, algo.value)()

    def _digest(self, m, hexdigest: T.Optional[bool]) -> T.Union[str, bytes]:
        if hexdigest is None:
            if self.hexdigest:
                return m.hexdigest()
            else:
                return m.digest()
        else:
            if hexdigest:
                return m.hexdigest()
            else:
                return m.digest()

    def of_str(
        self,
        s: str,
        algo: T.Optional[HashAlgoEnum] = None,
        hexdigest: T.Optional[bool] = None,
    ) -> T.Union[str, bytes]:
        """
        Return hash value of a string.
        """
        m = self._construct(algo)
        m.update(s.encode("utf-8"))
        return self._digest(m, hexdigest)

    def of_bytes(
        self,
        b: bytes,
        algo: T.Optional[HashAlgoEnum] = None,
        hexdigest: T.Optional[bool] = None,
    ) -> T.Union[str, bytes]:
        """
        Return hash value of a bytes.
        """
        m = self._construct(algo)
        m.update(b)
        return self._digest(m, hexdigest)

    def of_str_or_bytes(
        self,
        s_or_b: T.Union[bytes, str],
        algo: T.Optional[HashAlgoEnum] = None,
        hexdigest: T.Optional[bool] = None,
    ) -> T.Union[str, bytes]:
        """
        Return hash value of a bytes or string.
        """
        if isinstance(s_or_b, str):
            return self.of_str(s_or_b, algo, hexdigest)
        else:
            return self.of_bytes(s_or_b, algo, hexdigest)

    def of_file(
        self,
        abspath: str,
        nbytes: int = 0,
        chunk_size: int = 1024,
        algo: T.Optional[HashAlgoEnum] = None,
        hexdigest: T.Optional[bool] = None,
    ) -> T.Union[str, bytes]:
        """
        Return hash value of a file, or only a piece of a file
        """
        if nbytes < 0:
            raise ValueError("chunk_size cannot smaller than 0")
        if chunk_size < 1:
            raise ValueError("chunk_size cannot smaller than 1")
        if (nbytes > 0) and (nbytes < chunk_size):
            chunk_size = nbytes

        m = self._construct(algo)

        with open(abspath, "rb") as f:
            if nbytes:  # use first n bytes only
                have_reads = 0
                while True:
                    have_reads += chunk_size
                    if have_reads > nbytes:
                        n = nbytes - (have_reads - chunk_size)
                        if n:
                            data = f.read(n)
                            m.update(data)
                        break
                    else:
                        data = f.read(chunk_size)
                        m.update(data)
            else:  # use entire content
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    m.update(data)
        return self._digest(m, hexdigest)


hashes = Hashes()

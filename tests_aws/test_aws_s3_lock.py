# -*- coding: utf-8 -*-

import time
import moto

from datetime import datetime

import pytest

from fixa.aws.mock_test import BaseMockTest
from fixa.aws.aws_s3_lock import get_utc_now, Lock, Vault, AlreadyLockedError


class Test(BaseMockTest):
    mock_list = [
        moto.mock_s3,
    ]

    @classmethod
    def setup_class_post_hook(cls):
        cls.bucket = "my-bucket"
        cls.key = "lock.json"
        cls.bsm.s3_client.create_bucket(Bucket=cls.bucket)

    def _test_lock(self):
        lock = Lock(
            owner=None,
            lock_time="2000-01-01 00:00:00",
            release_time="2000-01-01 00:15:00",
            expire=900,
        )
        assert lock.is_locked(datetime(2000, 1, 1, 0, 15, 0), "alice") is False

        lock = Lock(
            owner="alice",
            lock_time="2000-01-01 00:00:00",
            release_time=None,
            expire=900,
        )
        assert lock.is_locked(datetime(2000, 1, 1, 0, 10, 0), "bob") is True
        assert lock.is_locked(datetime(2000, 1, 1, 0, 20, 0), "bob") is False

        assert lock.is_locked(datetime(2000, 1, 1, 0, 10, 0), "alice") is False
        assert lock.is_locked(datetime(2000, 1, 1, 0, 20, 0), "alice") is False

    def _test_vault_1(self):
        # create vault, at this moment, the lock doesn't exists yet
        vault = Vault(bucket=self.bucket, key=self.key, expire=900)

        # initialize a lock, the lock status should be "not locked"
        lock = vault._read(s3_client=self.bsm.s3_client)
        now = get_utc_now()
        assert lock.is_locked(now, "alice") is False

        # alice acquire the lock, now the lock status should be "locked by alice"
        lock = vault.acquire(self.bsm.s3_client, owner="alice")
        assert lock.owner == "alice"
        now = get_utc_now()
        assert lock.is_locked(now, "alice") is False
        assert lock.is_locked(now, "bob") is True

        # another people wants to acquire the lock, but it's already locked by alice
        with pytest.raises(AlreadyLockedError):
            vault.acquire(self.bsm.s3_client, owner=None)

        with pytest.raises(AlreadyLockedError):
            vault.acquire(self.bsm.s3_client, owner="bob")

        # if alice wants to acquire the lock again, it's ok
        lock = vault.acquire(self.bsm.s3_client, owner="alice")

        # alice release the lock, now the lock status should be "not locked"
        lock = vault.release(s3_client=self.bsm.s3_client, lock=lock)
        assert lock.owner is None
        now = get_utc_now()
        assert lock.is_locked(now, "alice") is False
        assert lock.is_locked(now, "bob") is False

    def _test_vault_2(self):
        # create vault, at this moment, the lock doesn't exists yet
        vault = Vault(bucket=self.bucket, key=self.key, expire=1, wait=0)

        # alice acquire the lock, now the lock status should be "locked by alice"
        lock = vault.acquire(self.bsm.s3_client, owner="alice")
        assert lock.owner == "alice"
        assert lock.expire == 1

        # from alice point of view, it is not locked
        now = get_utc_now()
        assert lock.is_locked(now, "alice") is False
        # from bob point of view, it is locked
        assert lock.is_locked(now, "bob") is True

        # but this time it is expired
        time.sleep(2)
        now = get_utc_now()
        assert lock.is_locked(now, "bob") is False

        lock = vault.acquire(self.bsm.s3_client, owner="bob")
        assert lock.owner == "bob"
        assert lock.expire == 1

    def test(self):
        print("")
        self._test_lock()
        self._test_vault_1()
        self._test_vault_2()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.aws_s3_lock", preview=False)

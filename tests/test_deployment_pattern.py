# -*- coding: utf-8 -*-

import pytest
from fixa.deployment_pattern import (
    RoutingConfig,
    InvalidCanaryIncrementsError,
    NextVersionMissingError,
    blue_green,
    canary,
)


def test_blue_green():
    rc = blue_green(next_version="1")
    assert rc.version1 == "1"
    assert rc.version1_weight == 100
    assert rc.version2 is None
    assert rc.version2_weight is None


def test_canary():
    with pytest.raises(InvalidCanaryIncrementsError):
        canary(canary_increments=[])
    with pytest.raises(InvalidCanaryIncrementsError):
        canary(canary_increments=[0, 100])
    with pytest.raises(InvalidCanaryIncrementsError):
        canary(canary_increments=[-1, 101])
    with pytest.raises(NextVersionMissingError):
        canary()
    with pytest.raises(NextVersionMissingError):
        canary(routing_config=RoutingConfig(version1="1"))

    rc = canary(
        canary_increments=[30, 70],
        next_version="1",
        routing_config=None,
    )
    assert rc.version1 == "1"
    assert rc.version2 is None

    rc = canary(
        canary_increments=[30, 70],
        next_version="2",
        routing_config=RoutingConfig(version1="1"),
    )
    assert rc.version1 == "2"
    assert rc.version2 == "1"
    assert rc.version1_weight == 30
    assert rc.version2_weight == 70

    rc = canary(
        canary_increments=[30, 70],
        next_version="3",
        routing_config=RoutingConfig(
            version1="2",
            version2="1",
            version2_weight=90,
        ),
    )
    assert rc.version1 == "2"
    assert rc.version2 == "1"
    assert rc.version1_weight == 30
    assert rc.version2_weight == 70

    rc = canary(
        canary_increments=[30, 70],
        next_version="3",
        routing_config=RoutingConfig(
            version1="2",
            version2="1",
            version2_weight=70,
        ),
    )
    assert rc.version1 == "2"
    assert rc.version2 == "1"
    assert rc.version1_weight == 70
    assert rc.version2_weight == 30

    rc = canary(
        canary_increments=[30, 70],
        next_version="3",
        routing_config=RoutingConfig(
            version1="2",
            version2="1",
            version2_weight=30,
        ),
    )
    assert rc.version1 == "2"
    assert rc.version2 is None
    assert rc.version1_weight == 100
    assert rc.version2_weight is None


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.deployment_pattern", preview=False)

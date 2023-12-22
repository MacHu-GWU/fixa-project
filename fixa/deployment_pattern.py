# -*- coding: utf-8 -*-

"""
This module implements the abstraction of blue/green, canary deployment.
Provides lots of utilities to help you manage the deployment process.

This module assumes that your app version is from 1, 2, 3, ... and so on.
For canary deployment, either you route 100% traffic to a version, either
you route x%, y% to a major version and a minor version. The concept of
major version is the target version you, it starts from very low percentage
of traffic, and gradually increase to 100%.

The concept of ``next_version`` is that
"if publish a new version, what is the version number should be?".
For example, if you haven't made any deployment yet, then the next version is "1".
If you have deployed version "1", then the next version is "2" (which does not exists yet).
"""

import typing as T
import dataclasses

__version__ = "0.1.1"


@dataclasses.dataclass
class RoutingConfig:
    """
    Canary deployment routing config.

    :param version1: version 1 identifier
    :param version2: version 2 identifier, if None, then all traffic goes to version 1
    :param version2_weight: version 2 weight, from 1 ~ 99.
    """

    version1: str = dataclasses.field()
    version2: T.Optional[str] = dataclasses.field(default=None)
    version2_weight: T.Optional[int] = dataclasses.field(default=None)

    def __post_init__(self):
        if self.version2_weight is not None:
            if (1 <= self.version2_weight <= 99) is False:
                raise ValueError("version2_weight must be between 1 and 99")

    @property
    def version1_weight(self) -> int:
        """
        :return: version 1 weight, from 1 ~ 100.
        """
        if self.version2_weight is None:
            return 100
        else:
            return 100 - self.version2_weight


def blue_green(next_version: str) -> RoutingConfig:
    """
    Find the routing config for next blue-green deployment.

    :param next_version: if publish a new version, what is the version number should be?

    :return: :class:RoutingConfig
    """
    return RoutingConfig(version1=str(next_version))


DEFAULT_CANARY_INCREMENTS = [25, 50, 75]


class InvalidCanaryIncrementsError(ValueError):
    pass


class NextVersionMissingError(ValueError):
    pass


def canary(
    canary_increments: T.Optional[T.List[int]] = None,
    next_version: T.Optional[str] = None,
    routing_config: T.Optional[RoutingConfig] = None,
) -> RoutingConfig:
    """
    Find the routing config for next canary deployment.

    :param canary_increments: a list of 1 ~ 100 integers, the weight of
        the major version will be gradually increased by these numbers.
    :param next_version: if publish a new version, what is the version number should be?
    :param routing_config: existing routing config, use None to indicate
        no existing routing config.

    :return: :class:RoutingConfig
    """
    if canary_increments is None:
        canary_increments = DEFAULT_CANARY_INCREMENTS

    if len(canary_increments) == 0:
        raise InvalidCanaryIncrementsError
    elif any([(i <= 1 or i >= 99) for i in canary_increments]):
        raise InvalidCanaryIncrementsError
    else:
        canary_increments.sort()

    # it's the first deployment, route all traffic to the next version
    if routing_config is None:
        if next_version is None:
            raise NextVersionMissingError(
                "next_version must be provided for the first deployment"
            )
        return RoutingConfig(version1=str(next_version))
    # it is in STABLE state (only one version), create a new canary deployment
    elif routing_config.version2 is None:
        if next_version is None:
            raise NextVersionMissingError(
                "next_version must be provided for a new canary deployment"
            )
        return RoutingConfig(
            version1=next_version,
            version2=routing_config.version1,
            version2_weight=100 - canary_increments[0],
        )
    # it is not in STABLE state (only one version), gradually increase major version to 100%
    else:
        for threshold in canary_increments:
            if routing_config.version1_weight < threshold:
                return RoutingConfig(
                    version1=routing_config.version1,
                    version2=routing_config.version2,
                    version2_weight=100 - threshold,
                )
        return RoutingConfig(
            version1=routing_config.version1,
        )

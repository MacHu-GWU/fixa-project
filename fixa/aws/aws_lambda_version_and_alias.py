# -*- coding: utf-8 -*-

"""
AWS Lambda version and alias management helper functions.

Requirements::

    boto3

Optional Requirements::

    boto3-stubs[lambda]

Usage example::

    from aws_lambda_version_and_alias import (
        LATEST,
        list_versions_by_function,
        version_dct_to_version_int,
        get_last_published_version,
        publish_version,
        keep_n_most_recent_versions,
        get_alias,
        RoutingConfig,
        DEFAULT_CANARY_INCREMENTS,
        InvalidCanaryIncrementsError,
        NextVersionMissingError,
        get_alias_routing_config,
        deploy_alias,
        delete_alias,
        new_routing_config_for_blue_green,
        new_routing_config_for_canary,
    )

This module is originally from https://github.com/MacHu-GWU/fixa-project/blob/main/fixa/aws/aws_lambda_version_and_alias.py
"""

import dataclasses
import typing as T

import botocore.exceptions

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda import LambdaClient
    from mypy_boto3_lambda.type_defs import (
        FunctionConfigurationTypeDef,
        AliasConfigurationResponseTypeDef,
    )

__version__ = "0.2.1"

LATEST = "$LATEST"


# ------------------------------------------------------------------------------
# Version
# ------------------------------------------------------------------------------
def list_versions_by_function(
    lbd_client: "LambdaClient",
    func_name: str,
    max_items: int = 9999,
) -> T.List[T.Union[dict, "FunctionConfigurationTypeDef"]]:
    """
    List all lambda function versions. Return a list of detail dict.
    The order of the versions is not guaranteed.

    :param lbd_client: ``boto3.client("lambda")`` object.
    :param func_name: lambda function name
    """
    paginator = lbd_client.get_paginator("list_versions_by_function")
    response_iterator = paginator.paginate(
        FunctionName=func_name,
        PaginationConfig={
            "MaxItems": max_items,
            "PageSize": 50,
        },
    )
    versions = []
    for response in response_iterator:
        versions.extend(response.get("Versions", []))
    return versions


def version_dct_to_version_int(versions: T.List[dict]) -> T.List[int]:
    """
    Convert a list of lambda function version detail dict to a list of
    version number. The $LATEST version is not included.
    """
    int_versions = []
    for dct in versions:
        try:
            int_versions.append(int(dct["Version"]))
        except:
            pass
    return int_versions


def get_last_published_version(
    lbd_client: "LambdaClient",
    func_name: str,
    max_items: int = 9999,
) -> T.Optional[int]:
    """
    Get the last published version number. If there's no published version,
    return None.

    :param lbd_client: ``boto3.client("lambda")`` object.
    :param func_name: lambda function name
    """
    versions = list_versions_by_function(lbd_client, func_name, max_items)
    int_versions = version_dct_to_version_int(versions)
    if int_versions:
        return max(int_versions)
    else:  # pragma: no cover
        return None


def publish_version(
    lbd_client: "LambdaClient",
    func_name: str,
) -> T.Tuple[bool, int]:
    """
    Publish a new version. The AWS official doc says that:
    Lambda doesn’t publish a version if the function’s configuration and
    code haven’t changed since the last version.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/publish_version.html

    :param lbd_client: ``boto3.client("lambda")`` object.
    :param func_name: lambda function name

    :return: a tuple of two items, first item is a boolean flag to indicate
        that if a new version is created. the second item is the version id.
        if there's a new version is created, return the new version, otherwise,
        return the latest version number.
    """
    last_published_version = get_last_published_version(lbd_client, func_name)
    if last_published_version is None:  # pragma: no cover
        last_published_version = -1
    res = lbd_client.publish_version(FunctionName=func_name)
    published_version = int(res["Version"])
    if last_published_version == published_version:
        return False, published_version
    else:
        return True, published_version


def keep_n_most_recent_versions(
    lbd_client: "LambdaClient",
    func_name: str,
    n: int,
    max_items: int = 9999,
) -> T.List[int]:
    """
    Only keep the most recent n versions, delete the rest of published versions.
    If a version is associated with an alias, it will not be deleted.

    :param lbd_client: ``boto3.client("lambda")`` object.
    :param func_name: lambda function name
    :param n: number of latest version to keep
    :param max_items: max number of versions to list in one request.
    """
    versions = list_versions_by_function(lbd_client, func_name, max_items)
    int_versions = version_dct_to_version_int(versions)
    int_versions.sort()
    versions_to_delete = int_versions[:-n]
    for version in versions_to_delete:
        try:
            lbd_client.delete_function(
                FunctionName=f"{func_name}:{version}",
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceConflictException":
                pass
            else:  # pragma: no cover
                raise e
    return versions_to_delete


# ------------------------------------------------------------------------------
# Alias
# ------------------------------------------------------------------------------
def get_alias(
    lbd_client: "LambdaClient",
    func_name: str,
    alias: str,
) -> T.Optional[T.Union[dict, "AliasConfigurationResponseTypeDef"]]:
    """
    Get alias detail dict. If the alias doesn't exist, return None.
    """
    try:
        return lbd_client.get_alias(FunctionName=func_name, Name=alias)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        else:  # pragma: no cover
            raise e


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

    @property
    def version1_weight(self) -> int:
        """
        :return: version 1 weight, from 1 ~ 100.
        """
        if self.version2_weight is None:
            return 100
        else:
            return 100 - self.version2_weight

    @classmethod
    def from_alias_detail(cls, alias_detail: dict):
        """
        Extract routing config from ``lbd_client.get_alias()`` API response.
        """
        version1 = alias_detail["FunctionVersion"]
        additional_version_weights = alias_detail.get("RoutingConfig", {}).get(
            "AdditionalVersionWeights", {}
        )
        if additional_version_weights:
            version2, version2_weight = list(additional_version_weights.items())[0]
            return cls(
                version1=version1,
                version2=version2,
                version2_weight=round(version2_weight * 100),
            )
        else:
            return cls(version1=version1)

    def to_update_alias_kwargs(self) -> dict:
        """
        Generate corresponding keyword arguments for ``lbd_client.update_alias()``
        or ``lbd_client.create_alias()``.
        """
        kwargs = dict(FunctionVersion=self.version1)
        if self.version2 is not None:
            kwargs["RoutingConfig"] = dict(
                AdditionalVersionWeights={
                    self.version2: round(self.version2_weight / 100, 2)
                }
            )
        return kwargs

    def to_deploy_alias_kwargs(self) -> dict:
        """
        Generate corresponding keyword arguments for :func:`deploy_alias`
        """
        kwargs = dict(version1=self.version1)
        if self.version2 is not None:
            kwargs["version2"] = self.version2
            kwargs["version2_percentage"] = round(self.version2_weight / 100, 2)
        return kwargs


def _blue_green(next_version: str) -> RoutingConfig:  # pragma: no cover
    """
    Find the routing config for next blue-green deployment.

    :param next_version: if publish a new version, what is the version number should be?

    :return: :class:RoutingConfig
    """
    return RoutingConfig(version1=str(next_version))


DEFAULT_CANARY_INCREMENTS = [25, 50, 75]


class InvalidCanaryIncrementsError(ValueError):  # pragma: no cover
    pass


class NextVersionMissingError(ValueError):  # pragma: no cover
    pass


def _canary(
    canary_increments: T.Optional[T.List[int]] = None,
    next_version: T.Optional[str] = None,
    routing_config: T.Optional[RoutingConfig] = None,
) -> RoutingConfig:  # pragma: no cover
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


def get_alias_routing_config(
    lbd_client: "LambdaClient",
    func_name: str,
    alias: str,
) -> T.Optional[RoutingConfig]:
    """
    The original get_alias API returns in this format::

        {
            'AliasArn': 'string',
            'Name': 'string',
            'FunctionVersion': 'string',
            'Description': 'string',
            'RoutingConfig': {
                'AdditionalVersionWeights': {
                    'string': 0.9
                }
            },
            'RevisionId': 'string'
        }

    We would like to convert into a object to show the version and weight::

        RoutingConfig(version1=..., version2=..., version2_weight=...)

    :param lbd_client: ``boto3.client("lambda")`` object.
    :param func_name: lambda function name
    :param alias: alias name

    :return: :class:`RoutingConfig`, if the alias doesn't exist, return None
    """
    res = get_alias(lbd_client, func_name, alias)
    if res is None: # pragma: no cover
        return res
    return RoutingConfig.from_alias_detail(res)


def deploy_alias(
    lbd_client: "LambdaClient",
    func_name: str,
    alias: str,
    description: T.Optional[str] = None,
    version1: T.Optional[T.Union[str, int]] = None,
    version2: T.Optional[T.Union[str, int]] = None,
    version2_percentage: T.Optional[float] = None,
) -> T.Tuple[bool, T.Optional[str]]:
    """
    Point the alias to the given version or split traffic between two versions.

    :param lbd_client: ``boto3.client("lambda")`` object.
    :param func_name: lambda function name
    :param alias: alias name
    :param description: description of the alias
    :param version1: the main version of the alias; if not specified, use $LATEST
    :param version2: the secondary version of the alias; if not specified, then
        the version1 will have 100% traffic; if specified, then version2_percentage
        also has to be specified.
    :param version2_percentage: if version2 is specified, then it has to be a
        value between 0.01 and 0.99.

    :return: a tuple of two items; first item is a boolean flag to indicate
        whether a creation or update is performed; second item is the alias
        revision id, if creation or update is not performed, then return None.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/get_alias.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/create_alias.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/update_alias.html
    """
    # find out the target version and resolve routing configuration
    if version1 is not None:
        version1 = str(version1)
    target_version = LATEST if version1 is None else version1

    # figure out the secondary version and routing configuration
    if version2 is not None:
        version2 = str(version2)
        if not (0.01 <= version2_percentage <= 0.99):  # pragma: no cover
            raise ValueError("version2 percentage has to be between 0.01 and 0.99.")
        if target_version == LATEST:  # pragma: no cover
            raise ValueError(
                "$LATEST is not supported for an alias pointing to more than 1 version."
            )
        routing_config = dict(AdditionalVersionWeights={version2: version2_percentage})
    else:
        routing_config = {}

    create_or_update_alias_kwargs = dict(
        FunctionName=func_name,
        Name=alias,
        FunctionVersion=target_version,
    )
    if description:  # pragma: no cover
        create_or_update_alias_kwargs["Description"] = description

    create_or_update_alias_kwargs["RoutingConfig"] = routing_config

    try:
        # check if the alias exists
        response = lbd_client.get_alias(
            FunctionName=func_name,
            Name=alias,
        )
        # if exists, compare the current live version with the target version
        current_version = response["FunctionVersion"]
        current_routing_config = response.get("RoutingConfig", {})
        # update the target version
        if (current_version != target_version) or (
            current_routing_config != routing_config
        ):
            res = lbd_client.update_alias(**create_or_update_alias_kwargs)
            return True, res["RevisionId"]
        else:
            return False, None
    except botocore.exceptions.ClientError as e:
        # if not exists, create it
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            res = lbd_client.create_alias(**create_or_update_alias_kwargs)
            return True, res["RevisionId"]
        else:  # pragma: no cover
            raise e


def delete_alias(
    lbd_client: "LambdaClient",
    func_name: str,
    alias: str,
) -> dict:
    """
    The original API is already idempotent, so no need to check if the alias exists.

    :param lbd_client: ``boto3.client("lambda")`` object.
    :param func_name: lambda function name
    :param alias: alias name
    """
    return lbd_client.delete_alias(
        FunctionName=func_name,
        Name=alias,
    )


def new_routing_config_for_blue_green(
    lbd_client: "LambdaClient",
    func_name: str,
) -> RoutingConfig:
    """
    Find the routing config for next blue-green deployment.
    """
    last_published_version = get_last_published_version(lbd_client, func_name)
    if last_published_version is None:
        next_version = str(1)
    else:
        next_version = str(last_published_version + 1)
    return _blue_green(next_version)


def new_routing_config_for_canary(
    lbd_client: "LambdaClient",
    func_name: str,
    alias: str,
    canary_increments: T.Optional[T.List[float]] = None,
) -> RoutingConfig:
    """
    Find the routing config for next canary deployment.

    It assumes that your app version is from 1, 2, 3, ... and so on.
    For canary deployment, either you route 100% traffic to a version, either
    you route x%, y% to a major version and a minor version. The concept of
    major version is the target version you, it starts from very low percentage
    of traffic, and gradually increase to 100%.

    The concept of ``next_version`` is that
    "if publish a new version, what is the version number should be?".
    For example, if you haven't made any deployment yet, then the next version is "1".
    If you have deployed version "1", then the next version is "2" (which does not exists yet).
    """
    last_published_version = get_last_published_version(lbd_client, func_name)
    if last_published_version is None:
        next_version = str(1)
    else:
        next_version = str(last_published_version + 1)
    routing_config = get_alias_routing_config(lbd_client, func_name, alias)
    return _canary(
        canary_increments,
        next_version,
        routing_config,
    )

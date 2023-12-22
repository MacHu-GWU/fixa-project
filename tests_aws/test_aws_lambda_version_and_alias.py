# -*- coding: utf-8 -*-

import time
import uuid

import boto3

from fixa.aws.aws_lambda_version_and_alias import (
    list_versions_by_function,
    version_dct_to_version_int,
    publish_version,
    keep_n_most_recent_versions,
    get_alias,
    get_alias_routing_config,
    deploy_alias,
    delete_alias,
    RoutingConfig,
    new_routing_config_for_blue_green,
    new_routing_config_for_canary,
)

aws_profile = "awshsh_app_dev_us_east_1"
func_name = "version_alias_test"
alias = "LIVE"

boto_ses = boto3.session.Session(profile_name=aws_profile)
lbd_client = boto_ses.client("lambda")


def _test_setup():
    delete_alias(lbd_client, func_name, alias)


def _test_publish_version():
    is_new_version_created, version = publish_version(lbd_client, func_name)
    is_new_version_created, version1 = publish_version(lbd_client, func_name)
    assert is_new_version_created is False
    assert version == version1

    lbd_client.update_function_configuration(
        FunctionName=func_name,
        Environment={
            "Variables": {
                "md5": uuid.uuid4().hex,
            }
        },
    )
    time.sleep(5)
    is_new_version_created, version2 = publish_version(lbd_client, func_name)
    assert is_new_version_created is True
    assert version2 == version1 + 1


def _test_keep_n_most_recent_versions():
    keep_n_most_recent_versions(lbd_client, func_name, 2)


def _test_deploy_alias():
    versions = list_versions_by_function(lbd_client, func_name)
    int_versions = version_dct_to_version_int(versions)
    int_versions.sort()
    is_alias_deployed, revision_id1 = deploy_alias(
        lbd_client,
        func_name,
        alias=alias,
        version1=int_versions[-2],
        version2=int_versions[-1],
        version2_percentage=0.1,
    )
    is_alias_deployed, revision_id2 = deploy_alias(
        lbd_client,
        func_name,
        alias=alias,
        version1=int_versions[-2],
        version2=int_versions[-1],
        version2_percentage=0.1,
    )
    assert is_alias_deployed is False
    assert revision_id2 is None

    is_alias_deployed, revision_id3 = deploy_alias(
        lbd_client,
        func_name,
        alias=alias,
        version1=int_versions[-2],
        version2=int_versions[-1],
        version2_percentage=0.9,
    )
    assert is_alias_deployed is True
    assert revision_id2 != revision_id3


def _test_delete_alias():
    delete_alias(lbd_client, func_name, alias)
    delete_alias(lbd_client, func_name, alias)
    assert get_alias(lbd_client, func_name, alias) is None


def _test_deployment_pattern():
    def _publish_version():
        lbd_client.update_function_configuration(
            FunctionName=func_name,
            Environment={
                "Variables": {
                    "md5": uuid.uuid4().hex,
                }
            },
        )
        time.sleep(5)
        publish_version(lbd_client, func_name)

    def _deploy_alias(rc: RoutingConfig):
        deploy_alias(
            lbd_client,
            func_name,
            alias,
            **rc.to_deploy_alias_kwargs(),
        )

    # blue/green, create new version
    rc = new_routing_config_for_blue_green(lbd_client, func_name)
    _publish_version()
    _deploy_alias(rc)
    rc1 = get_alias_routing_config(lbd_client, func_name, alias)

    # blue/green, create new version, version + 1
    rc = new_routing_config_for_blue_green(lbd_client, func_name)
    _publish_version()
    _deploy_alias(rc)
    rc2 = get_alias_routing_config(lbd_client, func_name, alias)
    assert int(rc2.version1) == int(rc1.version1) + 1

    # canary,
    rc = new_routing_config_for_canary(lbd_client, func_name, alias)
    _publish_version()
    _deploy_alias(rc)
    rc3 = get_alias_routing_config(lbd_client, func_name, alias)
    assert rc3 == rc
    assert rc3.version1_weight == 25

    rc = new_routing_config_for_canary(lbd_client, func_name, alias)
    _deploy_alias(rc)
    rc3 = get_alias_routing_config(lbd_client, func_name, alias)
    assert rc3 == rc
    assert rc3.version1_weight == 50

    rc = new_routing_config_for_canary(lbd_client, func_name, alias)
    _deploy_alias(rc)
    rc3 = get_alias_routing_config(lbd_client, func_name, alias)
    assert rc3 == rc
    assert rc3.version1_weight == 75

    rc = new_routing_config_for_canary(lbd_client, func_name, alias)
    _deploy_alias(rc)
    rc3 = get_alias_routing_config(lbd_client, func_name, alias)
    assert rc3 == rc
    assert rc3.version1_weight == 100


def test():
    _test_setup()
    _test_publish_version()
    _test_keep_n_most_recent_versions()
    _test_deploy_alias()
    _test_delete_alias()
    _test_deployment_pattern()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.aws_lambda_version_and_alias", preview=False)

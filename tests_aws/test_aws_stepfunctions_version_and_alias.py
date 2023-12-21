# -*- coding: utf-8 -*-

import time
import json
import uuid

import boto3
import botocore.exceptions

from fixa.aws.aws_stepfunctions_version_and_alias import (
    list_state_machine_versions,
    version_dct_to_version_int,
    publish_version,
    keep_n_most_recent_versions,
    deploy_alias,
    delete_alias,
)

aws_profile = "awshsh_app_dev_us_east_1"
sm_name = "version_alias_test1"
alias = "LIVE"

boto_ses = boto3.session.Session(profile_name=aws_profile)
sfn_client = boto_ses.client("stepfunctions")
aws_account_id = boto_ses.client("sts").get_caller_identity()["Account"]
sm_arn = f"arn:aws:states:us-east-1:{aws_account_id}:stateMachine:{sm_name}"
role_arn = f"arn:aws:iam::{aws_account_id}:role/sfn-admin-role"
sfn_alias_arn = f"{sm_arn}:{alias}"


def make_def(description: str = "no description"):
    return {
        "Comment": description,
        "StartAt": "Pass",
        "States": {"Pass": {"Type": "Pass", "End": True}},
    }


def create_init_sfn():
    try:
        sfn_client.create_state_machine(
            name=sm_name,
            definition=json.dumps(make_def()),
            roleArn=role_arn,
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "StateMachineAlreadyExists":
            pass
        else:
            raise e


def delete_sfn():
    sfn_client.delete_state_machine(stateMachineArn=sm_arn)


def _test_setup():
    delete_sfn()
    create_init_sfn()


def _test_publish_version():
    is_new_version_created, version = publish_version(sfn_client, sm_arn)
    is_new_version_created, version1 = publish_version(sfn_client, sm_arn)
    assert is_new_version_created is False
    assert version == version1

    sfn_client.update_state_machine(
        stateMachineArn=sm_arn,
        definition=json.dumps(make_def(f"new version {uuid.uuid4().hex}")),
    )
    time.sleep(10)
    is_new_version_created, version2 = publish_version(sfn_client, sm_arn)
    assert is_new_version_created is True
    assert version2 == version1 + 1


def _test_keep_n_most_recent_versions():
    keep_n_most_recent_versions(sfn_client, sm_arn, 2, skip_in_use_version=True)


def _test_deploy_alias():
    delete_alias(sfn_client, sfn_alias_arn)

    versions = list_state_machine_versions(sfn_client, sm_arn)
    int_versions = version_dct_to_version_int(versions)
    int_versions.sort()

    # use v1
    is_alias_deployed, routing_config = deploy_alias(
        sfn_client,
        sm_arn,
        alias=alias,
        version1=int_versions[-2],
    )
    assert is_alias_deployed is True
    assert routing_config == {int_versions[-2]: 100}

    is_alias_deployed, routing_config = deploy_alias(
        sfn_client,
        sm_arn,
        alias=alias,
        version1=int_versions[-2],
        delay=3,
    )
    assert is_alias_deployed is False
    assert routing_config is None

    # use v2
    is_alias_deployed, routing_config = deploy_alias(
        sfn_client,
        sm_arn,
        alias=alias,
    )
    assert is_alias_deployed is True
    assert routing_config == {int_versions[-1]: 100}

    is_alias_deployed, routing_config = deploy_alias(
        sfn_client,
        sm_arn,
        alias=alias,
        delay=3,
    )
    assert is_alias_deployed is False
    assert routing_config is None

    # use 99% of v1, 1% of v2
    is_alias_deployed, routing_config = deploy_alias(
        sfn_client,
        sm_arn,
        alias=alias,
        version1=int_versions[-2],
        version2=int_versions[-1],
        version2_percentage=1,
    )
    assert is_alias_deployed is True
    assert routing_config == {int_versions[-2]: 99, int_versions[-1]: 1}

    is_alias_deployed, routing_config = deploy_alias(
        sfn_client,
        sm_arn,
        alias=alias,
        version1=int_versions[-2],
        version2=int_versions[-1],
        version2_percentage=99,
        delay=3,
    )
    assert is_alias_deployed is True
    assert routing_config == {int_versions[-2]: 1, int_versions[-1]: 99}


def _test_delete_alias():
    delete_alias(sfn_client, sfn_alias_arn)
    delete_alias(sfn_client, sfn_alias_arn)


def test():
    """
    Workflow:

    1. create an initial state machine if not exists.
    2. test the publish_version() function, it will create at least 2 versions, v1, and v2
        v2 is the latest one.
    3. test the keep_n_most_recent_versions() function, it will keep the latest 2 versions,
    4. test the deploy_alias() function, it will update the routing multiple times.
    5. test the delete_alias() function, it will delete the alias.
    """
    # _test_setup()
    _test_publish_version()
    _test_keep_n_most_recent_versions()
    _test_deploy_alias()
    _test_delete_alias()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(
        __file__, "fixa.aws.aws_stepfunctions_version_and_alias", preview=False
    )

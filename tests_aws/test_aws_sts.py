# -*- coding: utf-8 -*-

import boto3
from fixa.aws.aws_sts import (
    mask_user_id,
    mask_aws_account_id,
    mask_iam_principal_arn,
    get_caller_identity,
    get_account_alias,
    get_account_info,
    print_account_info,
)


def test_mask_user_id():
    assert mask_user_id("A1B2C3D4GABCDEFGHIJKL") == "A1B2***IJKL"


def test_mask_aws_account_id():
    assert mask_aws_account_id("123456789012") == "12********12"


def test_mask_iam_principal_arn():
    assert (
        mask_iam_principal_arn("arn:aws:iam::123456789012:root")
        == "arn:aws:iam::12********12:root"
    )
    assert (
        mask_iam_principal_arn("arn:aws:iam::123456789012:role/role-name")
        == "arn:aws:iam::12********12:role/role-name"
    )
    assert (
        mask_iam_principal_arn(
            "arn:aws:iam::123456789012:role/service-role/AWSEC2ServiceRole"
        )
        == "arn:aws:iam::12********12:role/service-role/AWSEC2ServiceRole"
    )


def test_get_caller_identity():
    user_id, account_id, arn = get_caller_identity(boto3.client("sts"))
    assert "*" in user_id
    assert "*" in account_id
    assert "*" in arn


def test_get_account_alias():
    acc_alias = get_account_alias(boto3.client("iam"))
    # print(acc_alias)


def test_print_account_info():
    boto_ses = boto3.session.Session()
    print_account_info(boto_ses)


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.aws_sts", preview=False)

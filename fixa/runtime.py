# -*- coding: utf-8 -*-

"""
Usage example:

.. code-block:: python

    from fixa.runtime import (
        IS_LOCAL,
        IS_CODEBUILD,
        IS_JENKINS,
        IS_CI,
        IS_AWS_LAMBDA,
        IS_AWS_EC2,
        IS_AWS_BATCH,
        IS_AWS_GLUE,
        IS_AWS_CLOUD9,
    )
"""

import os

IS_LOCAL = False
IS_CODEBUILD = False
IS_JENKINS = False
IS_CI = False
IS_AWS_LAMBDA = False
IS_AWS_EC2 = False
IS_AWS_BATCH = False
IS_AWS_GLUE = False
IS_AWS_CLOUD9 = False


# ref:
# - codebuild: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
if "CODEBUILD_BUILD_ID" in os.environ:  # pragma: no cover
    IS_CODEBUILD = True
    IS_CI = True

# ref:
# - github action: https://docs.github.com/en/actions/learn-github-actions/variables
# - gitlab ci: https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
# - bitbucket: https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
# - circleci: https://circleci.com/docs/variables/
if "CI" in os.environ:  # pragma: no cover
    IS_CI = True

# ref:
# - jenkins: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables
if "BUILD_TAG" in os.environ and "EXECUTOR_NUMBER" in os.environ:  # pragma: no cover
    IS_JENKINS = True
    IS_CI = True

# ref: https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html
if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:  # pragma: no cover
    IS_AWS_LAMBDA = True

# ref: https://docs.aws.amazon.com/batch/latest/userguide/job_env_vars.html
if "AWS_BATCH_JOB_ID" in os.environ:  # pragma: no cover
    IS_AWS_BATCH = True

if "--JOB_RUN_ID" in os.environ:  # pragma: no cover
    IS_AWS_GLUE = True

if "C9" in os.environ:  # pragma: no cover
    IS_AWS_CLOUD9 = True

if (
    IS_CI is False
    and IS_AWS_LAMBDA is False
    and IS_AWS_BATCH is False
    and IS_AWS_GLUE is False
    and IS_AWS_CLOUD9 is False
):
    IS_LOCAL = True

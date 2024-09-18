# -*- coding: utf-8 -*-

"""
This module implements the automation to work with AWS codeartifact code repository.
"""

# --- standard library
import typing as T
import dataclasses
import os
import shutil
import subprocess
import contextlib
from pathlib import Path

# --- third party library (include vendor)
import botocore.exceptions


__version__ = "0.1.1"


@contextlib.contextmanager
def temp_cwd(path: T.Union[str, Path]):
    """
    Temporarily set the current working directory (CWD) and automatically
    switch back when it's done.

    Example:

    .. code-block:: python

        with temp_cwd(Path("/path/to/target/working/directory")):
            # do something
    """
    path = Path(path).absolute()
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a dir!")
    cwd = os.getcwd()
    os.chdir(str(path))
    try:
        yield path
    finally:
        os.chdir(cwd)


def print_command(args: T.List[str]):
    cmd = " ".join(args)
    print(f"run command: {cmd}")


def get_codeartifact_repository_endpoint(
    codeartifact_client,
    aws_codeartifact_domain: str,
    aws_codeartifact_repository: str,
) -> str:
    """
    reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codeartifact/client/get_authorization_token.html
    """
    res = codeartifact_client.get_repository_endpoint(
        domain=aws_codeartifact_domain,
        repository=aws_codeartifact_repository,
        format="pypi",
    )
    return res["repositoryEndpoint"]


def get_codeartifact_authorization_token(
    codeartifact_client,
    aws_codeartifact_domain: str,
) -> str:
    """
    reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codeartifact/client/get_authorization_token.html
    """
    res = codeartifact_client.get_authorization_token(
        domain=aws_codeartifact_domain,
    )
    return res["authorizationToken"]


@dataclasses.dataclass
class CodeArtifactContext:
    package_name: str = dataclasses.field()
    aws_account_id: str = dataclasses.field()
    aws_region: str = dataclasses.field()
    aws_codeartifact_domain: str = dataclasses.field()
    aws_codeartifact_repository: str = dataclasses.field()
    dir_project_root: Path = dataclasses.field()
    path_bin_aws: T.Optional[Path] = dataclasses.field(default=None)
    path_bin_twine: T.Optional[Path] = dataclasses.field(default=None)
    path_bin_pip: T.Optional[Path] = dataclasses.field(default=None)
    path_bin_poetry: T.Optional[Path] = dataclasses.field(default=None)

    @property
    def normalized_package_name(self) -> str:
        return self.package_name.replace("_", "-")

    @property
    def poetry_secondary_source_name(self) -> str:
        return self.aws_codeartifact_repository.replace("-", "_")

    @property
    def dir_dist(self) -> Path:
        return self.dir_project_root.joinpath("dist")

    def poetry_source_add_codeartifact(
        self,
        codeartifact_client,
    ):
        """
        Run:

        .. code-block:: bash

            poetry source add --secondary ${source_name} "https://${domain_name}-${aws_account_id}.d.codeartifact.${aws_region}.amazonaws.com/pypi/${repository_name}/simple/"
        """
        endpoint = get_codeartifact_repository_endpoint(
            codeartifact_client=codeartifact_client,
            aws_codeartifact_domain=self.aws_codeartifact_domain,
            aws_codeartifact_repository=self.aws_codeartifact_repository,
        )
        args = [
            f"{self.path_bin_poetry}",
            "source",
            "add",
            "--priority=supplemental",
            self.poetry_secondary_source_name,
            f"{endpoint}simple/",
        ]
        print_command(args)
        subprocess.run(args, check=True)

    def poetry_authorization(
        self,
        codeartifact_client,
    ):
        """
        Set environment variables to allow Poetry to authenticate with CodeArtifact.
        """
        token = get_codeartifact_authorization_token(
            codeartifact_client=codeartifact_client,
            aws_codeartifact_domain=self.aws_codeartifact_domain,
        )
        source_name = self.poetry_secondary_source_name.upper()
        os.environ[f"POETRY_HTTP_BASIC_{source_name}_USERNAME"] = "aws"
        os.environ[f"POETRY_HTTP_BASIC_{source_name}_PASSWORD"] = token

    def twine_authorization(
        self,
        aws_profile: T.Optional[str] = None,
    ):
        """
        Run

        .. code-block:: bash

            aws codeartifact login --tool twine \
                --domain ${domain_name} \
                --domain-owner ${aws_account_id} \
                --repository ${repo_name} \
                --profile ${aws_profile}

        Reference:

        - `Configure and use twine with CodeArtifact <https://docs.aws.amazon.com/codeartifact/latest/ug/python-configure-twine.html>`_
        - `AWS CodeArtifact CLI <https://docs.aws.amazon.com/cli/latest/reference/codeartifact/index.html>`_
        """
        args = [
            f"{self.path_bin_aws}",
            "codeartifact",
            "login",
            "--tool",
            "twine",
            "--domain",
            self.aws_codeartifact_domain,
            "--domain-owner",
            self.aws_account_id,
            "--repository",
            self.aws_codeartifact_repository,
        ]
        if aws_profile:
            args.extend(["--profile", aws_profile])

        print_command(args)
        subprocess.run(args, check=True)

    def twine_upload(
        self,
        aws_profile: T.Optional[str] = None,
    ):
        """
        Upload Python package to CodeArtifact.

        Run

        .. code-block:: bash

            twine upload dist/* --repository codeartifact
        """
        console_url = (
            f"https://{self.aws_region}.console.aws.amazon.com/codesuite/codeartifact/d"
            f"/{self.aws_account_id}/{self.aws_codeartifact_domain}/r"
            f"/{self.aws_codeartifact_repository}/p/pypi/"
            f"{self.package_name}/versions?region={self.aws_region}"
        )
        print(f"preview in AWS CodeArtifact console: {console_url}")
        self.twine_authorization(aws_profile=aws_profile)
        args = ["twine", "upload", f"{self.dir_dist}/*", "--repository", "codeartifact"]
        print_command(args)
        with temp_cwd(self.dir_project_root):
            subprocess.run(args, check=True)

    def poetry_build(self):
        shutil.rmtree(self.dir_dist, ignore_errors=True)
        args = [
            f"{self.path_bin_poetry}",
            "build",
        ]
        print_command(args)
        with temp_cwd(self.dir_project_root):
            subprocess.run(args, check=True)

    def publish_to_codeartifact(
        self,
        codeartifact_client,
        package_version: str,
    ):
        """
        Publish your Python package to AWS CodeArtifact.
        """
        try:
            res = codeartifact_client.describe_package_version(
                domain=self.aws_codeartifact_domain,
                repository=self.aws_codeartifact_repository,
                format="pypi",
                package=self.normalized_package_name,
                packageVersion=package_version,
            )
            message = (
                f"package {self.normalized_package_name!r} "
                f"= {package_version} already exists!"
            )
            raise Exception(message)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                pass
            else:
                raise e

        self.poetry_build()
        self.twine_upload()

    def remove_from_codeartifact(
        self,
        codeartifact_client,
        package_version: str,
    ):
        """
        Publish your Python package to AWS CodeArtifact.
        """
        # try:
        res = input(
            f"Are you sure you want to remove the package {self.normalized_package_name!r} "
            f"version {package_version!r}? (Y/N): "
        )
        if res == "Y":
            res = codeartifact_client.delete_package_versions(
                domain=self.aws_codeartifact_domain,
                repository=self.aws_codeartifact_repository,
                format="pypi",
                package=self.normalized_package_name,
                versions=[package_version],
                expectedStatus="Published",
            )
            print("Package version removed.")
        else:
            print("Aborted")

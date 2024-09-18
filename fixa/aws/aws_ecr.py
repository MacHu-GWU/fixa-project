# -*- coding: utf-8 -*-

"""
This module implements the automation to build and push container image for ECR.
"""

import typing as T
import os
import base64
import contextlib
import subprocess
import dataclasses
from pathlib import Path

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


def get_ecr_repo_uri(
    aws_account_id: str,
    aws_region: str,
    ecr_repo_name: str,
    tag: str,
) -> str:
    """
    Get the full ECR repo URI with image tag.
    """
    return f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo_name}:{tag}"


def get_ecr_auth_token(
    ecr_client,
    aws_account_id: str,
) -> T.Tuple[str, str]:
    """
    Get ECR auth token using boto3 SDK.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/get_authorization_token.html

    :return: username and password
    """
    res = ecr_client.get_authorization_token(
        registryIds=[aws_account_id],
    )
    b64_token = res["authorizationData"][0]["authorizationToken"]
    user_pass = base64.b64decode(b64_token.encode("utf-8")).decode("utf-8")
    username, password = user_pass.split(":", 1)
    return username, password


def docker_login(
    username: str,
    password: str,
    registry_url: str,
) -> bool:
    """
    Login docker cli to AWS ECR. Run:

    .. code-block:: bash

        echo ${password} | docker login -u ${username} --password-stdin ${registry_url}

    :return: a boolean flag to indicate if the login is successful.
    """
    args = ["echo", password]
    pipe = subprocess.Popen(args, stdout=subprocess.PIPE)
    args = ["docker", "login", "-u", username, registry_url, "--password-stdin"]
    response = subprocess.run(args, stdin=pipe.stdout, capture_output=True)
    text = response.stdout.decode("utf-8")
    is_succeeded = "Login Succeeded" in text
    return is_succeeded


def ecr_login(
    ecr_client,
    aws_account_id: str,
    aws_region: str,
) -> bool:
    """
    Login docker cli to AWS ECR using boto3 SDK and AWS CLI.

    :return: a boolean flag to indicate if the login is successful.
    """
    registry_url = (
        f"https://{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
    )
    username, password = get_ecr_auth_token(
        ecr_client=ecr_client,
        aws_account_id=aws_account_id,
    )
    return docker_login(username, password, registry_url)


@dataclasses.dataclass
class EcrContext:
    """
    A utility class to help build and push docker image to ECR.

    :param aws_account_id: The AWS account id of your ECR repo.
    :param aws_region: The AWS region of your ECR repo
    :param repo_name: the repo name
    :param dir_dockerfile: the directory where the Dockerfile is located.
    """

    aws_account_id: str = dataclasses.field()
    aws_region: str = dataclasses.field()
    repo_name: str = dataclasses.field()
    path_dockerfile: Path = dataclasses.field()

    @classmethod
    def new(
        cls,
        aws_account_id: str,
        aws_region: str,
        repo_name: str,
        path_dockerfile: Path,
    ):
        """
        Create a new instance of EcrContext.

        :param ecr_client: ``boto3.client("ecr")`` object.
        :param repo_name: ECR repo name.
        :param path_dockerfile: the path to the Dockerfile.
        """
        return cls(
            aws_account_id=aws_account_id,
            aws_region=aws_region,
            repo_name=repo_name,
            path_dockerfile=path_dockerfile,
        )

    @property
    def dir_dockerfile(self) -> Path:
        return self.path_dockerfile.parent

    def get_image_uri(self, tag: str) -> str:
        """
        Get the ECR container image URI.

        :param tag: the container image tag.
        """
        return f"{self.aws_account_id}.dkr.ecr.{self.aws_region}.amazonaws.com/{self.repo_name}:{tag}"

    def build_image(
        self,
        image_tag_list: T.Optional[T.List[str]] = None,
        additional_args: T.Optional[T.List[str]] = None,
    ):
        """
        Build docker image.

        :param image_tag_list: the list of tag you want to give to the built image,
        e.g. ["latest", "0.1.1"]
        :param additional_args: additional command line arguments for ``docker build ...``

        .. note::

            If you are trying to build a linux/amd64 compatible image on an ARM chip Mac
            you need to set ``"--platform=linux/amd64"`` in the ``additional_args``.
        """
        if image_tag_list is None:
            image_tag_list = ["latest"]
        if additional_args is None:
            additional_args = []
        with temp_cwd(self.dir_dockerfile):
            args = ["docker", "build"]
            # Reference: https://docs.docker.com/engine/reference/commandline/build/#tag
            for tag in image_tag_list:
                args.extend(["-t", self.get_image_uri(tag)])
            args.extend(additional_args)
            args.append(".")
            # don't use check=True
            # the args may include sensitive information like aws credentials
            # we don't want to automatically print to the log
            # instead, we want to handle the error our self.
            result = subprocess.run(args)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    "'docker build' command did not exit successfully!",
                )

    def push_image(
        self,
        image_tag_list: T.Optional[T.List[str]] = None,
        additional_args: T.Optional[T.List[str]] = None,
    ):
        """
        Push Docker image to ECR.
        """
        if image_tag_list is None:
            image_tag_list = ["latest"]
        if additional_args is None:
            additional_args = []
        with temp_cwd(self.dir_dockerfile):
            for tag in image_tag_list:
                args = [
                    "docker",
                    "push",
                    self.get_image_uri(tag),
                ]
                args.extend(additional_args)
                subprocess.run(args, check=True)

    def test_image(
        self,
        tag: T.Optional[str] = None,
        additional_args: T.Optional[T.List[str]] = None,
    ):
        """
        Test the container image locally by running it.

        :param additional_args: additional command line arguments for ``docker run ...``
        """
        if tag is None:
            tag = "latest"
        if additional_args is None:
            additional_args = []
        with temp_cwd(self.dir_dockerfile):
            image_uri = self.get_image_uri(tag)
            args = [
                "docker",
                "run",
                "--rm",
                image_uri,
            ]
            args.extend(additional_args)
            subprocess.run(args, check=True)

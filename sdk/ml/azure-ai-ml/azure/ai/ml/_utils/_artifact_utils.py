# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import hashlib
import logging
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import Iterable, List, Optional, Union

from typing_extensions import Literal

from azure.ai.ml.constants._common import DefaultOpenEncoding

from ._http_utils import HttpPipeline
from .utils import get_base_directory_for_cache

_logger = logging.getLogger(__name__)


class ArtifactCache:
    """Disk cache of azure artifact packages.

    The key of the cache is path of artifact packages in local, like this
    azure-ai-ml/components/additional_includes/artifacts/{organization}/{project}/{feed}/{package_name}/{version}.
    The value is the files/folders in this cache folder.
    """

    # artifact cache is shared across SDK versions and across workspaces/registries
    DEFAULT_DISK_CACHE_DIRECTORY = get_base_directory_for_cache().joinpath(
        "components",
        "additional_includes",
        "artifacts",
    )
    POSTFIX_CHECKSUM = "checksum"
    _instance_lock = Lock()
    _instance = None

    def __new__(cls):
        """Singleton creation disk cache."""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = object.__new__(cls)
                    cls.check_artifact_extension()
        return cls._instance

    @staticmethod
    def check_artifact_extension():
        # check az extension azure-devops installed. Install it if not installed.
        result = subprocess.run(
            [shutil.which("az"), "artifacts", "--help", "--yes"],
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Auto-installation failed. Please install azure-devops "
                "extension by 'az extension add --name azure-devops'."
            )

    def __init__(self, cache_directory=None):
        self._cache_directory = cache_directory or self.DEFAULT_DISK_CACHE_DIRECTORY
        Path(self._cache_directory).mkdir(exist_ok=True, parents=True)
        self._artifacts_tool_path = None
        self._download_locks = defaultdict(Lock)

    @property
    def cache_directory(self) -> Path:
        """Cache directory path.

        :return: The cache directory
        :rtype: Path
        """
        return self._cache_directory

    @staticmethod
    def hash_files_content(file_list: List[Union[str, os.PathLike]]) -> str:
        """Hash the file content in the file list.

        :param file_list: The list of files to hash
        :type file_list: List[Union[str, os.PathLike]]
        :return: Hashed file contents
        :rtype: str
        """
        ordered_file_list = copy.copy(file_list)
        hasher = hashlib.sha256()
        ordered_file_list.sort()
        for item in ordered_file_list:
            with open(item, "rb") as f:
                hasher.update(f.read())
        return hasher.hexdigest()

    @staticmethod
    def _format_organization_name(organization):
        pattern = r'[<>:"\\/|?*]'
        normalized_organization_name = re.sub(pattern, "_", organization)
        return normalized_organization_name

    @staticmethod
    def get_organization_project_by_git():
        """Get organization and project from git remote url. For example, the git remote url is
        "https://organization.visualstudio.com/xxx/project_name/_git/repositry_name" or
        "https://dev.azure.com/{organization}/project".

        :return organization_url, project: organization_url, project
        :rtype organization_url, project: str, str
        """
        result = subprocess.run(
            [shutil.which("git"), "config", "--get", "remote.origin.url"],
            capture_output=True,
            encoding="utf-8",
            check=False,
        )

        if result.returncode != 0:
            # When organization and project cannot be retrieved from the origin url.
            raise RuntimeError(
                f"Get the git origin url failed, you must be in a local Git directory, "
                f"error message: {result.stderr}"
            )
        origin_url = result.stdout.strip()

        # Organization URL has two format, https://dev.azure.com/{organization} and
        # https://{organization}.visualstudio.com
        # https://docs.microsoft.com/en-us/azure/devops/extend/develop/work-with-urls?view=azure-devops&tabs=http
        if "dev.azure.com" in origin_url:
            regex = r"^https:\/\/\w*@?dev\.azure\.com\/(\w*)\/(\w*)"
            results = re.findall(regex, origin_url)
            if results:
                organization, project = results[0]
                return f"https://dev.azure.com/{organization}", project
        elif "visualstudio.com" in origin_url:
            regex = r"https:\/\/(\w*)\.visualstudio\.com.*\/(\w*)\/_git"
            results = re.findall(regex, origin_url)
            if results:
                organization, project = results[0]
                return f"https://{organization}.visualstudio.com", project

        # When organization and project cannot be retrieved from the origin url.
        raise RuntimeError(
            f'Cannot get organization and project from git origin url "{origin_url}", '
            f'you must be in a local Git directory that has a "remote" referencing a '
            f"Azure DevOps or Azure DevOps Server repository."
        )

    @classmethod
    def _get_checksum_path(cls, path):
        artifact_path = Path(path)
        return artifact_path.parent / f"{artifact_path.name}_{cls.POSTFIX_CHECKSUM}"

    def _redirect_artifacts_tool_path(self, organization: Optional[str]):
        """Downloads the artifacts tool and redirects `az artifact` command to it.

        Done to avoid the transient issue when download artifacts

        :param organization:  The organization url. If None, is determined by local git repo
        :type organization: Optional[str]
        """
        from azure.identity import DefaultAzureCredential

        if not organization:
            organization, _ = self.get_organization_project_by_git()

        organization_pattern = r"https:\/\/(.*)\.visualstudio\.com"
        result = re.findall(pattern=organization_pattern, string=organization)
        if result:
            organization_name = result[0]
        else:
            organization_pattern = r"https:\/\/dev\.azure\.com\/(.*)"
            result = re.findall(pattern=organization_pattern, string=organization)
            if not result:
                raise RuntimeError("Cannot find artifact organization.")
            organization_name = result[0]

        if not self._artifacts_tool_path:
            os_name = "Windows" if os.name == "nt" else "Linux"
            credential = DefaultAzureCredential()
            token = credential.get_token("https://management.azure.com/.default")
            header = {"Authorization": "Bearer " + token.token}

            # The underlying HttpTransport is meant to be user configurable.
            # MLClient instances have a user configured Pipeline for sending http requests
            # TODO: Replace this with MlCLient._requests_pipeline
            requests_pipeline = HttpPipeline()
            url = (
                f"https://{organization_name}.vsblob.visualstudio.com/_apis/clienttools/ArtifactTool/release?"
                f"osName={os_name}&arch=AMD64"
            )
            response = requests_pipeline.get(  # pylint: disable=too-many-function-args,unexpected-keyword-arg
                url, headers=header
            )
            if response.status_code == 200:
                artifacts_tool_path = tempfile.mktemp()  # nosec B306
                artifacts_tool_uri = response.json()["uri"]
                response = requests_pipeline.get(artifacts_tool_uri)  # pylint: disable=too-many-function-args
                with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
                    zip_file.extractall(artifacts_tool_path)
                os.environ["AZURE_DEVOPS_EXT_ARTIFACTTOOL_OVERRIDE_PATH"] = str(artifacts_tool_path.resolve())
                self._artifacts_tool_path = artifacts_tool_path
            else:
                _logger.warning("Download artifact tool failed: %s", response.text)

    def _download_artifacts(
        self,
        download_cmd: Iterable[str],
        organization: Optional[str],
        name: str,
        version: str,
        feed: str,
        max_retries: int = 3,
    ):
        """Download artifacts with retry.

        :param download_cmd: The command used to download the artifact
        :type download_cmd: Iterable[str]
        :param organization: The artifact organization
        :type organization: Optional[str]
        :param name: The package name
        :type name: str
        :param version: The package version
        :type version: str
        :param feed: The download feed
        :type feed: str
        :param max_retries: The number of times to retry the download. Defaults to 3
        :type max_retries: int
        """
        retries = 0
        while retries <= max_retries:
            try:
                self._redirect_artifacts_tool_path(organization)
            except Exception as e:  # pylint: disable=W0718
                _logger.warning("Redirect artifacts tool path failed, details: %s", e)

            retries += 1
            result = subprocess.run(
                download_cmd,
                capture_output=True,
                encoding="utf-8",
                check=False,
            )

            if result.returncode != 0:
                error_msg = (
                    f"Download package {name}:{version} from the feed {feed} failed {retries} times: {result.stderr}"
                )
                if retries < max_retries:
                    _logger.warning(error_msg)
                else:
                    error_msg = error_msg + f"\nDownload artifact debug info: {result.stdout}"
                    raise RuntimeError(error_msg)
            else:
                return

    def _check_artifacts(self, artifact_package_path: Union[str, os.PathLike]) -> bool:
        """Check the artifact folder is legal.

        :param artifact_package_path: The artifact package path
        :type artifact_package_path: Union[str, os.PathLike]
        :return:
          * If the artifact folder or checksum file does not exist, return false.
          * If the checksum file exists and does not equal to the hash of artifact folder, return False.
          * If the checksum file equals to the hash of artifact folder, return true.
        :rtype: bool
        """
        path = Path(artifact_package_path)
        if not path.exists():
            return False
        checksum_path = self._get_checksum_path(artifact_package_path)
        if checksum_path.exists():
            with open(checksum_path, "r", encoding=DefaultOpenEncoding.READ) as f:
                checksum = f.read()
                file_list = [os.path.join(root, f) for root, _, files in os.walk(path) for f in files]
                artifact_hash = self.hash_files_content(file_list)
                return checksum == artifact_hash
        return False

    def get(
        self,
        feed: str,
        name: str,
        version: str,
        scope: Literal["project", "organization"],
        organization: Optional[str] = None,
        project: Optional[str] = None,
        resolve: bool = True,
    ) -> Optional[Path]:
        """Get the catch path of artifact package. Package path like this azure-ai-
        ml/components/additional_includes/artifacts/{organization}/{project}/{feed}/{package_name}/{version}. If the
        path exits, it will return the package path. If the path not exist and resolve=True, it will download the
        artifact package and return package path. If the path not exist and resolve=False, it will return None.

        :param feed: Name or ID of the feed.
        :type feed: str
        :param name: Name of the package.
        :type name: str
        :param version: Version of the package.
        :type version: str
        :param scope: Scope of the feed: 'project' if the feed was created in a project, and 'organization' otherwise.
        :type scope: Literal["project", "organization"]
        :param organization: Azure DevOps organization URL.
        :type organization: str
        :param project: Name or ID of the project.
        :type project: str
        :param resolve: Whether download package when package does not exist in local.
        :type resolve: bool
        :return artifact_package_path: Cache path of the artifact package
        :rtype: Optional[Path]
        """
        if not all([organization, project]):
            org_val, project_val = self.get_organization_project_by_git()
            organization = organization or org_val
            project = project or project_val
        artifact_package_path = (
            Path(self.DEFAULT_DISK_CACHE_DIRECTORY)
            / self._format_organization_name(organization)
            / project
            / feed
            / name
            / version
        )
        # Use lock to avoid downloading the same package at the same time.
        with self._download_locks[artifact_package_path]:
            if self._check_artifacts(artifact_package_path):
                # When the cache folder of artifact package exists, it's sure that the package has been downloaded.
                return artifact_package_path.absolute().resolve()
            if resolve:
                check_sum_path = self._get_checksum_path(artifact_package_path)
                if Path(check_sum_path).exists():
                    os.unlink(check_sum_path)
                if artifact_package_path.exists():
                    # Remove invalid artifact package to avoid affecting download artifact.
                    temp_folder = tempfile.mktemp()  # nosec B306
                    os.rename(artifact_package_path, temp_folder)
                    shutil.rmtree(temp_folder)
                # Download artifact
                return self.set(
                    feed=feed,
                    name=name,
                    version=version,
                    organization=organization,
                    project=project,
                    scope=scope,
                )
        return None

    def set(
        self,
        feed: str,
        name: str,
        version: str,
        scope: Literal["project", "organization"],
        organization: Optional[str] = None,
        project: Optional[str] = None,
    ) -> Path:
        """Set the artifact package to the cache. The key of the cache is path of artifact packages in local. The value
        is the files/folders in this cache folder. If package path exists, directly return package path.

        :param feed: Name or ID of the feed.
        :type feed: str
        :param name: Name of the package.
        :type name: str
        :param version: Version of the package.
        :type version: str
        :param scope: Scope of the feed: 'project' if the feed was created in a project, and 'organization' otherwise.
        :type scope: Literal["project", "organization"]
        :param organization: Azure DevOps organization URL.
        :type organization: str
        :param project: Name or ID of the project.
        :type project: str
        :return artifact_package_path: Cache path of the artifact package
        :rtype: Path
        """
        tempdir = tempfile.mktemp()  # nosec B306
        download_cmd = [
            shutil.which("az"),
            "artifacts",
            "universal",
            "download",
            "--feed",
            feed,
            "--name",
            name,
            "--version",
            version,
            "--scope",
            scope,
            "--path",
            tempdir,
        ]
        if organization:
            download_cmd.extend(["--org", organization])
        if project:
            download_cmd.extend(["--project", project])
        _logger.info("Start downloading artifacts %s:%s from %s.", name, version, feed)
        result = subprocess.run(
            download_cmd,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )

        if result.returncode != 0:
            artifacts_tool_not_find_error_pattern = "No such file or directory: .*artifacttool"
            if re.findall(artifacts_tool_not_find_error_pattern, result.stderr):
                # When download artifacts tool failed retry download artifacts command
                _logger.warning(
                    "Download package %s:%s from the feed %s failed: %s", name, version, feed, result.stderr
                )
                download_cmd.append("--debug")
                self._download_artifacts(download_cmd, organization, name, version, feed)
            else:
                raise RuntimeError(f"Download package {name}:{version} from the feed {feed} failed: {result.stderr}")
        try:
            # Copy artifact package from temp folder to the cache path.
            if not all([organization, project]):
                org_val, project_val = self.get_organization_project_by_git()
                organization = organization or org_val
                project = project or project_val
            artifact_package_path = (
                Path(self.DEFAULT_DISK_CACHE_DIRECTORY)
                / self._format_organization_name(organization)
                / project
                / feed
                / name
                / version
            )
            artifact_package_path.parent.mkdir(exist_ok=True, parents=True)
            file_list = [os.path.join(root, f) for root, _, files in os.walk(tempdir) for f in files]
            artifact_hash = self.hash_files_content(file_list)
            os.rename(tempdir, artifact_package_path)
            temp_checksum_file = os.path.join(tempfile.mkdtemp(), f"{version}_{self.POSTFIX_CHECKSUM}")
            with open(temp_checksum_file, "w", encoding=DefaultOpenEncoding.WRITE) as f:
                f.write(artifact_hash)
            os.rename(
                temp_checksum_file,
                artifact_package_path.parent / f"{version}_{self.POSTFIX_CHECKSUM}",
            )
        except (FileExistsError, PermissionError, OSError):
            # On Windows, if dst exists a FileExistsError is always raised.
            # On Unix, if dst is a non-empty directory, an OSError is raised.
            # If dst is being used by another process will raise PermissionError.
            # https://docs.python.org/3/library/os.html#os.rename
            pass
        return artifact_package_path.absolute().resolve()

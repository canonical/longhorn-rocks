#
# Copyright 2024 Canonical, Ltd.
#

import logging
import sys

import pytest
from k8s_test_harness.util import docker_util, env_util, platform_util

LOG: logging.Logger = logging.getLogger(__name__)

LOG.addHandler(logging.FileHandler(f"{__name__}.log"))
LOG.addHandler(logging.StreamHandler(sys.stdout))


IMAGE_NAME = "longhorn-instance-manager"
IMAGE_VERSIONS = ["v1.7.0"]


@pytest.mark.abort_on_fail
@pytest.mark.parametrize("image_version", IMAGE_VERSIONS)
def test_check_rock_image_contents(image_version):
    """Test ROCK contains same fileset as original image."""

    architecture = platform_util.get_current_rockcraft_platform_architecture()

    rock_meta = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, architecture
    )
    rock_image = rock_meta.image
    original_image = f"longhornio/longhorn-instance-manager:{image_version}"

    dir_to_check = "/usr/local/bin"

    original_image_files = docker_util.list_files_under_container_image_dir(
        original_image, root_dir=dir_to_check
    )
    rock_image_files = docker_util.list_files_under_container_image_dir(
        rock_image, root_dir=dir_to_check
    )

    rock_fileset = set(rock_image_files)
    original_fileset = set(original_image_files)

    original_extra_files = original_fileset - rock_fileset
    if original_extra_files:
        pytest.fail(
            f"Missing some files from the original image: " f"{original_extra_files}"
        )

    rock_extra_files = rock_fileset - original_fileset
    if rock_extra_files:
        pytest.fail(
            f"Rock has extra files not present in original image: "
            f"{rock_extra_files}"
        )

    # Check auxiliary binaries:
    binary_paths_to_check = [
        f"/usr/sbin/{bin}"
        for bin in [
            "tgt-admin",
            "tgt-setup-lun",
            "tgtadm",
            "tgtd",
            "tgtimg",
        ]
    ]
    binary_paths_to_check.append("/usr/local/sbin/nvme")
    binary_paths_to_check.append("/tini")

    docker_util.ensure_image_contains_paths(
        rock_image,
        binary_paths_to_check,
    )

    process = docker_util.run_in_docker(rock_image, ["nvme", "version"])
    assert "nvme version 2.9.1" in process.stdout
    assert "libnvme version 1.9" in process.stdout

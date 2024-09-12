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


IMAGE_NAME = "longhorn-engine"
IMAGE_VERSIONS = ["v1.6.2", "v1.7.0"]


@pytest.mark.abort_on_fail
@pytest.mark.parametrize("image_version", IMAGE_VERSIONS)
def test_check_rock_image_contents(image_version):
    """Test ROCK contains same fileset as original image."""

    architecture = platform_util.get_current_rockcraft_platform_architecture()

    rock_meta = env_util.get_build_meta_info_for_rock_version(
        IMAGE_NAME, image_version, architecture
    )
    rock_image = rock_meta.image

    binary_paths_to_check = [
        f"/usr/local/bin/{bin}"
        for bin in [
            "longhorn",
            "longhorn-instance-manager",
            "launch-simple-longhorn",
            "engine-manager",
            "launch-simple-file",
            "tgt-admin",
            "tgt-setup-lun",
            "tgtadm",
            "tgtd",
            "tgtimg",
        ]
    ]
    binary_paths_to_check.append("/tini")

    docker_util.ensure_image_contains_paths(
        rock_image,
        binary_paths_to_check,
    )

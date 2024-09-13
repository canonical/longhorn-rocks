#
# Copyright 2024 Canonical, Ltd.
#

import pytest
from k8s_test_harness.util import docker_util, env_util

ROCK_EXPECTED_FILES = [
    "/usr/local/sbin/launch-manager",
    "/usr/local/sbin/longhorn-manager",
    "/usr/local/sbin/nsmounter",
]


@pytest.mark.parametrize("image_version", ["v1.6.2", "v1.7.0"])
def test_longhorn_manager_rock(image_version):
    """Test longhorn-manager rock."""
    rock = env_util.get_build_meta_info_for_rock_version(
        "longhorn-manager", image_version, "amd64"
    )
    image = rock.image

    # check rock filesystem.
    docker_util.ensure_image_contains_paths(image, ROCK_EXPECTED_FILES)

    # check binary.
    process = docker_util.run_in_docker(image, ["longhorn-manager", "--version"])
    assert f"longhorn-manager version {image_version}" in process.stdout

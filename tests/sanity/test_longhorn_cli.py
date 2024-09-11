#
# Copyright 2024 Canonical, Ltd.
#

import pytest
from k8s_test_harness.util import docker_util, env_util

ROCK_EXPECTED_FILES = [
    "/spdk",
    "/usr/local/sbin/longhornctl",
    "/usr/local/sbin/longhornctl-local",
]


@pytest.mark.parametrize("image_version", ["v1.7.0"])
def test_longhorn_cli_rock(image_version):
    """Test longhorn-cli rock."""
    rock = env_util.get_build_meta_info_for_rock_version(
        "longhorn-cli", image_version, "amd64"
    )
    image = rock.image

    # check rock filesystem.
    docker_util.ensure_image_contains_paths(image, ROCK_EXPECTED_FILES)

    # check binaries and their versions.
    process = docker_util.run_in_docker(image, ["longhornctl", "version"])
    assert image_version in process.stdout

    process = docker_util.run_in_docker(image, ["longhornctl-local", "version"])
    assert image_version in process.stdout

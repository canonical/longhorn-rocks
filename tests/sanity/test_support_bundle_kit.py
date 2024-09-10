#
# Copyright 2024 Canonical, Ltd.
#

import pytest
from k8s_test_harness.util import docker_util, env_util

ROCK_EXPECTED_FILES = [
    "/tmp/common",
    "/usr/bin/entrypoint.sh",
    "/usr/bin/collector-harvester",
    "/usr/bin/collector-k3os",
    "/usr/bin/collector-longhorn",
    "/usr/bin/collector-sle-micro-rancher",
    "/usr/bin/support-bundle-collector.sh",
    "/usr/bin/support-bundle-kit",
]


@pytest.mark.parametrize("image_version", ["v0.0.41"])
def test_support_bundle_kit_rock(image_version):
    """Test support-bundle-kit rock."""
    rock = env_util.get_build_meta_info_for_rock_version(
        "support-bundle-kit", image_version, "amd64"
    )
    image = rock.image

    # check rock filesystem.
    docker_util.ensure_image_contains_paths(image, ROCK_EXPECTED_FILES)

    # check expected executables.
    # the script calls tini, which should have a specific version we're expecting.
    process = docker_util.run_in_docker(image, ["entrypoint.sh"], False)
    assert "tini version 0.19.0" in process.stderr

    process = docker_util.run_in_docker(image, ["yq", "--help"])
    assert "yq is a portable command-line data file processor" in process.stdout

    process = docker_util.run_in_docker(image, ["support-bundle-kit", "version"])
    assert "v0.0.41" in process.stdout

#
# Copyright 2024 Canonical, Ltd.
#

import pytest
from k8s_test_harness.util import docker_util, env_util

ROCK_EXPECTED_FILES = [
    "/etc/dbus-1/system.d/org.ganesha.nfsd.conf",
    "/etc/ld.so.conf.d/local_libs.conf",
    "/etc/mtab",
    "/etc/nsswitch.conf",
    "/export",
    "/longhorn-share-manager",
    "/usr/local/bin/ganesha.nfsd",
    "/var/run/dbus",
]


@pytest.mark.parametrize("image_version", ["v1.7.0"])
def test_longhorn_share_manager_rock(image_version):
    """Test longhorn-share-manager rock."""
    rock = env_util.get_build_meta_info_for_rock_version(
        "longhorn-share-manager", image_version, "amd64"
    )
    image = rock.image

    # check rock filesystem.
    docker_util.ensure_image_contains_paths(image, ROCK_EXPECTED_FILES)

    process = docker_util.run_in_docker(
        image, ["cat", "/etc/ld.so.conf.d/local_libs.conf"]
    )
    assert "/usr/local/lib64" in process.stdout

    process = docker_util.run_in_docker(image, ["cat", "/etc/nsswitch.conf"])
    assert "systemd" not in process.stdout

    process = docker_util.run_in_docker(image, ["ls", "-l", "/etc/mtab"])
    assert "/etc/mtab -> /proc/mounts" in process.stdout

    # check binaries.
    process = docker_util.run_in_docker(image, ["/longhorn-share-manager", "--help"])
    assert "longhorn-share-manager - A new cli application" in process.stdout

    process = docker_util.run_in_docker(image, ["ganesha.nfsd", "-v"])
    assert "NFS-Ganesha Release = V5.9" in process.stdout

#
# Copyright 2024 Canonical, Ltd.
#

import pytest
from k8s_test_harness.util import docker_util, env_util

ROCK_EXPECTED_FILES = [
    "/bin/pebble",
    "/etc/nginx/nginx.conf.template",
    "/entrypoint.sh",
    "/var/config/nginx",
    "/var/lib/nginx",
    "/var/log/nginx",
    "/var/run/nginx.pid",
    "/web",
]


@pytest.mark.parametrize("image_version", ["v1.7.0"])
def test_longhorn_ui_rock(image_version):
    """Test longhorn-ui rock."""
    rock = env_util.get_build_meta_info_for_rock_version(
        "longhorn-ui", image_version, "amd64"
    )
    image = rock.image

    # check rock filesystem.
    docker_util.ensure_image_contains_paths(image, ROCK_EXPECTED_FILES)

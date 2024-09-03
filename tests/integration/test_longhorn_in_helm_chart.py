#
# Copyright 2024 Canonical, Ltd.
#

import json
import logging
import sys

import pytest
from k8s_test_harness import harness
from k8s_test_harness.util import constants, env_util, k8s_util, platform_util

LOG: logging.Logger = logging.getLogger(__name__)

LOG.addHandler(logging.FileHandler(f"{__name__}.log"))
LOG.addHandler(logging.StreamHandler(sys.stdout))


IMAGE_VERSIONS = ["v1.7.0"]
# TODO(aznashwan): enable previous version testing too:
# IMAGE_VERSIONS = ["v1.6.2", "v1.7.0"]
CHART_RELEASE_URL = "https://github.com/longhorn/charts/releases/download/longhorn-1.7.0/longhorn-1.7.0.tgz"
INSTALL_NAME = "longhorn"

LONGHORN_AUX_IMAGES_VERSION_MAP = {
    # https://github.com/longhorn/longhorn/releases/download/v1.7.0/longhorn-images.txt
    "v1.7.0": {
        "support-bundle-kit": "v0.0.41",
        "csi-attacher": "v4.6.1",
        "csi-node-driver-registrar": "v2.11.1",
        "csi-resizer": "v1.11.1",
        "csi-snapshotter": "v7.0.2",
        "livenessprobe": "v2.13.1",
        "openshift-origin-oauth-proxy": "4.15",
    }
}

# This mapping indicates which fields of the upstream Longhorn Helm chart
# contain the 'image' fields which should be overridden with the ROCK
# image URLs and version during testing.
# https://github.com/longhorn/charts/blob/v1.7.x/charts/longhorn/values.yaml#L38-L109
IMAGE_NAMES_TO_CHART_VALUES_OVERRIDES_MAP = {
    "longhorn-engine": "longhorn.engine",
    "longhorn-manager": "longhorn.manager",
    "longhorn-ui": "longhorn.ui",
    "longhorn-instance-manager": "longhorn.instanceManager",
    "longhorn-share-manager": "longhorn.shareManager",
    "backing-image-manager": "longhorn.backingImageManager",
    "support-bundle-kit": "longhorn.supportBundleKit",
    "csi-attacher": "csi.attacher",
    "csi-provisioner": "csi.provisioner",
    "csi-node-driver-registrar": "csi.nodeDriverRegistrar",
    "csi-resizer": "csi.resizer",
    "csi-snapshotter": "csi.snapshotter",
    "livenessprobe": "csi.livenessProbe",
    "openshift-origin-oauth-proxy": "openshift.oauthProxy",
}


@pytest.mark.parametrize("image_version", IMAGE_VERSIONS)
def test_longhorn_helm_chart_deployment(
    function_instance: harness.Instance, image_version: str
):

    architecture = platform_util.get_current_rockcraft_platform_architecture()

    # Compose the Helm command line args for overriding the
    # image fields for each component:
    all_chart_value_overrides_args = []
    found_env_rocks_metadata = []
    all_rocks_meta_info = env_util.get_rocks_meta_info_from_env()

    # NOTE(aznashwan): GitHub actions UI sometimes truncates env values:
    LOG.info(
        f"All built rocks metadata from env was: "
        f"{json.dumps([rmi.__dict__ for rmi in all_rocks_meta_info])}"
    )

    for rmi in all_rocks_meta_info:
        if rmi.name in IMAGE_NAMES_TO_CHART_VALUES_OVERRIDES_MAP and (
            rmi.version == image_version and rmi.arch == architecture
        ):
            chart_section = IMAGE_NAMES_TO_CHART_VALUES_OVERRIDES_MAP[rmi.name]
            repo, tag = rmi.image.split(":")
            all_chart_value_overrides_args.extend(
                [
                    "--set",
                    f"image.{chart_section}.repository={repo}",
                    "--set",
                    f"image.{chart_section}.tag={tag}",
                ]
            )
            found_env_rocks_metadata.append(rmi.name)

    helm_command = [
        "sudo",
        "k8s",
        "helm",
        "install",
        INSTALL_NAME,
        CHART_RELEASE_URL,
    ]
    helm_command.extend(all_chart_value_overrides_args)

    function_instance.exec(helm_command)

    # HACK(aznashwan): all the Longhorn deployment resources in the chart
    # take a while to be properly set up, so we provide a generous wait:
    retry_kwargs = {"retry_times": 30, "retry_delay_s": 10}

    daemonsets = [
        "longhorn-csi-plugin",
        "longhorn-manager",
    ]
    for daemonset in daemonsets:
        k8s_util.wait_for_daemonset(
            function_instance,
            daemonset,
            **retry_kwargs,
        )

    deployments = [
        "csi-attacher",
        "csi-provisioner",
        "csi-resizer",
        "csi-snapshotter",
        "longhorn-driver-deployer",
        "longhorn-ui",
    ]
    for deployment in deployments:
        k8s_util.wait_for_deployment(
            function_instance,
            deployment,
            condition=constants.K8S_CONDITION_AVAILABLE,
            **retry_kwargs,
        )

#
# Copyright 2024 Canonical, Ltd.
#

import json
import logging
import pathlib
import sys
import time

import pytest
from k8s_test_harness import harness
from k8s_test_harness.util import constants, env_util, k8s_util, platform_util

LOG: logging.Logger = logging.getLogger(__name__)

LOG.addHandler(logging.FileHandler(f"{__name__}.log"))
LOG.addHandler(logging.StreamHandler(sys.stdout))

DIR = pathlib.Path(__file__).absolute().parent
TEMPLATES_DIR = DIR / ".." / "templates"

CSI_VOLUME_ANNOTATION = "csi.volume.kubernetes.io/nodeid"
LONGHORN_CSI_ANNOTATION_VALUE = "driver.longhorn.io"

IMAGE_VERSIONS = ["v1.6.2", "v1.7.0"]
CHART_RELEASE_URL = "https://github.com/longhorn/charts/releases/download/longhorn-%(version)s/longhorn-%(version)s.tgz"
INSTALL_NAME = "longhorn"
INSTALL_NS = "longhorn"


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
}

LONGHORN_CSI_IMAGES_VERSION_MAP = {
    # https://github.com/longhorn/longhorn/releases/download/v1.6.2/longhorn-images.txt
    "v1.6.2": {
        # helm image subsection: image
        "csi.attacher": "ghcr.io/canonical/csi-attacher:4.5.1-ck4",
        "csi.provisioner": "ghcr.io/canonical/csi-provisioner:3.6.4-ck0",
        "csi.nodeDriverRegistrar": "ghcr.io/canonical/csi-node-driver-registrar:2.9.2-ck1",
        "csi.resizer": "ghcr.io/canonical/csi-resizer:1.10.1-ck6",
        "csi.snapshotter": "ghcr.io/canonical/csi-snapshotter:6.3.4-ck1",
        "csi.livenessProbe": "ghcr.io/canonical/livenessprobe:2.12.0-ck6",
    },
    # https://github.com/longhorn/longhorn/releases/download/v1.7.0/longhorn-images.txt
    "v1.7.0": {
        # helm image subsection: image
        "csi.attacher": "ghcr.io/canonical/csi-attacher:4.6.1-ck5",
        "csi.provisioner": "ghcr.io/canonical/csi-provisioner:4.0.1-ck4",
        "csi.nodeDriverRegistrar": "ghcr.io/canonical/csi-node-driver-registrar:2.11.1-ck3",
        "csi.resizer": "ghcr.io/canonical/csi-resizer:1.11.1-ck1",
        "csi.snapshotter": "ghcr.io/canonical/csi-snapshotter:7.0.2-ck2",
        "csi.livenessProbe": "ghcr.io/canonical/livenessprobe:2.13.1-ck0",
    },
}


def _wait_for_node_annotation(instance, annotation, value):
    escaped_annotation = annotation.translate(str.maketrans({".": "\\.", "/": "\\/"}))
    jsonpath = f"jsonpath='{{.items[0].metadata.annotations.{escaped_annotation}}}'"

    annotated = False
    for i in range(10):
        process = instance.exec(
            ["k8s", "kubectl", "get", "nodes", "-o", jsonpath],
            capture_output=True,
            text=True,
        )

        if value in process.stdout:
            annotated = True
            break

        time.sleep(5)

    assert annotated, f"Expected node to have annotation '{annotation}={value}'."


def _wait_for_longhorn(instance: harness.Instance):
    # HACK(aznashwan): all the Longhorn deployment resources in the chart
    # take a while to be properly set up, so we provide a generous wait:
    retry_kwargs = {"retry_times": 30, "retry_delay_s": 10}

    daemonsets = [
        "longhorn-csi-plugin",
        "longhorn-manager",
    ]
    for daemonset in daemonsets:
        k8s_util.wait_for_daemonset(
            instance,
            daemonset,
            INSTALL_NS,
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
            instance,
            deployment,
            INSTALL_NS,
            condition=constants.K8S_CONDITION_AVAILABLE,
            **retry_kwargs,
        )

    # Wait until the node gets annotated with driver.longhorn.io, meaning that the Longhorn CSI
    # plugin was successfully registered.
    _wait_for_node_annotation(
        instance, CSI_VOLUME_ANNOTATION, LONGHORN_CSI_ANNOTATION_VALUE
    )


def _get_helm_command(image_version: str):
    architecture = platform_util.get_current_rockcraft_platform_architecture()

    # Compose the Helm command line args for overriding the
    # image fields for each component:
    all_rocks_meta_info = env_util.get_rocks_meta_info_from_env()

    # NOTE(aznashwan): GitHub actions UI sometimes truncates env values:
    LOG.info(
        f"All built rocks metadata from env was: "
        f"{json.dumps([rmi.__dict__ for rmi in all_rocks_meta_info])}"
    )

    images = []
    for rmi in all_rocks_meta_info:
        if rmi.name in IMAGE_NAMES_TO_CHART_VALUES_OVERRIDES_MAP and (
            rmi.version == image_version and rmi.arch == architecture
        ):
            chart_section = IMAGE_NAMES_TO_CHART_VALUES_OVERRIDES_MAP[rmi.name]
            images.append(k8s_util.HelmImage(rmi.image, subitem=chart_section))

    images += [
        k8s_util.HelmImage(image, subitem=subsection)
        for subsection, image in LONGHORN_CSI_IMAGES_VERSION_MAP[image_version].items()
    ]

    # include the version in the url, but without the leading 'v'.
    chart_url = CHART_RELEASE_URL % {"version": image_version[1:]}
    helm_command = k8s_util.get_helm_install_command(
        INSTALL_NAME, chart_url, INSTALL_NS, images=images
    )

    return helm_command


@pytest.mark.parametrize("image_version", IMAGE_VERSIONS)
def test_longhorn_helm_chart_deployment(
    function_instance: harness.Instance, image_version: str
):

    # Install prerequisites.
    base_url = f"https://raw.githubusercontent.com/longhorn/longhorn/{image_version}/deploy/prerequisite"
    for yaml_file in [
        "longhorn-iscsi-installation.yaml",
        "longhorn-nfs-installation.yaml",
    ]:
        url = f"{base_url}/{yaml_file}"
        process = function_instance.exec(
            ["k8s", "kubectl", "apply", "-f", url], check=True
        )

    # Deploy Longhorn through a helm chart.
    helm_command = _get_helm_command(image_version)
    function_instance.exec(helm_command)

    # Wait for Longhorn to become active,
    _wait_for_longhorn(function_instance)

    # Deploy nginx Pods with PVCs, which should be satisfied by Longhorn.
    for yaml_file in ["nginx-pod.yaml", "nginx-nfs-pod.yaml"]:
        function_instance.exec(
            ["k8s", "kubectl", "apply", "-f", "-"],
            input=pathlib.Path(TEMPLATES_DIR / yaml_file).read_bytes(),
        )

    # Expect the Pods to become ready, and that they have the volume attached.
    expected_outputs = {
        "nginx-longhorn-example": "ext4   /var/www /dev/longhorn/pvc-",
        "nginx-longhorn-nfs-example": "nfs4   /var/www ",
    }
    for pod_name, expected_output in expected_outputs.items():
        k8s_util.wait_for_resource(
            function_instance,
            "pod",
            pod_name,
            condition=constants.K8S_CONDITION_READY,
        )

        process = function_instance.exec(
            [
                "k8s",
                "kubectl",
                "exec",
                pod_name,
                "--",
                "bash",
                "-c",
                "findmnt /var/www -o FSTYPE,TARGET,SOURCE",
            ],
            capture_output=True,
            text=True,
        )

        assert expected_output in process.stdout

# Canonical ROCKs for Longhorn v1.6.2

Aim to be compatible with following upstream images
[listed in the v1.6.2 release of Longhorn](https://github.com/longhorn/longhorn/releases/download/v1.6.2/longhorn-images.txt).

* longhornio/longhorn-engine:v1.6.2
* longhornio/longhorn-manager:v1.6.2
* longhornio/longhorn-ui:v1.6.2
* longhornio/longhorn-instance-manager:v1.6.2
* longhornio/longhorn-share-manager:v1.6.2
* longhornio/backing-image-manager:v1.6.2
* longhornio/support-bundle-kit:v0.0.37

The CSI components required by Longhorn can be found here: https://github.com/canonical/csi-rocks.

The CSI rocks required for a Longhorn v1.6.2 deplyoment are:

* ghcr.io/canonical/csi-attacher:v4.5.1
* ghcr.io/canonical/csi-provisioner:v3.6.4
* ghcr.io/canonical/csi-node-driver-registrar:v2.9.2
* ghcr.io/canonical/csi-resizer:v1.10.1
* ghcr.io/canonical/csi-snapshotter:v6.3.4
* ghcr.io/canonical/livenessprobe:v2.12.0

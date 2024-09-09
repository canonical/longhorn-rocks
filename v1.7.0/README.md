# Canonical ROCKs for Longhorn v1.7.0

Aim to be compatible with following upstream images:

* longhornio/longhorn-engine:v1.7.0
* longhornio/longhorn-manager:v1.7.0
* longhornio/longhorn-ui:v1.7.0
* longhornio/longhorn-instance-manager:v1.7.0
* longhornio/longhorn-share-manager:v1.7.0
* longhornio/backing-image-manager:v1.7.0
* longhornio/support-bundle-kit:v0.0.41

The CSI components required by Longhorn can be found here: https://github.com/canonical/csi-rocks. The rocks required by Longhorn v1.7.0 are:

* ghcr.io/canonical/csi-attacher:4.6.1-ck5
* ghcr.io/canonical/csi-provisioner:4.0.1-ck4
* ghcr.io/canonical/csi-node-driver-registrar:2.11.1-ck3
* ghcr.io/canonical/csi-resizer:1.11.1-ck1
* ghcr.io/canonical/csi-snapshotter:7.0.2-ck2
* ghcr.io/canonical/livenessprobe:2.13.1-ck0

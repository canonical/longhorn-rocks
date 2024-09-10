# longhorn-rocks

OCI images for [Longhorn](https://longhorn.io) components built using [rockcraft](https://github.com/canonical/rockcraft).

Images are meant to be Ubuntu-based drop-in replacements for the following
upstream images:

* longhornio/longhorn-engine
* longhornio/longhorn-manager
* longhornio/longhorn-ui
* longhornio/longhorn-instance-manager
* longhornio/longhorn-share-manager
* longhornio/backing-image-manager
* longhornio/support-bundle-kit

The CSI components required by Longhorn can be found here: https://github.com/canonical/csi-rocks. The repository contains the rock equivalent of the following images:

* longhornio/csi-attacher
* longhornio/csi-provisioner
* longhornio/csi-node-driver-registrar
* longhornio/csi-resizer
* longhornio/csi-snapshotter
* longhornio/livenessprobe

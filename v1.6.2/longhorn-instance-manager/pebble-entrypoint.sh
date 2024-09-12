#!/bin/bash

# Required to prevent Pebble from considering the service to have
# exited too quickly to be worth restarting or respecting the
# "on-failure: shutdown" directive and thus hanging indefinitely:
# https://github.com/canonical/pebble/issues/240#issuecomment-1599722443
sleep 1.1

# NOTE(aznashwan): the longhorn-instance-manager image includes a number of
# dynamically-linked binaries which the instance-manager exec's.
# These binaries require some external libraries which must be indexed:
ldconfig

TINI_ARGS="$@"
if [ $# -eq 0 ]; then
    # https://github.com/longhorn/longhorn-instance-manager/blob/v1.6.2/package/Dockerfile#L146
    # https://github.com/longhorn/longhorn-instance-manager/pull/664
    TINI_ARGS="longhorn-instance-manager"
fi

# https://github.com/longhorn/longhorn-instance-manager/blob/v1.6.2/package/Dockerfile#L144
exec /tini -- $TINI_ARGS

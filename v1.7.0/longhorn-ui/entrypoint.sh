#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
set -x

cp -r /etc/nginx/* /var/config/nginx/
envsubst '${LONGHORN_MANAGER_IP},${LONGHORN_UI_PORT}' < /etc/nginx/nginx.conf.template > /var/config/nginx/nginx.conf

nginx -c /var/config/nginx/nginx.conf -g 'daemon off;'

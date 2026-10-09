#!/bin/bash
set -e

if [ "$DEBUGPY" = "wait" ]; then
    echo "===>Starting Odoo with debugpy (wait-for-client) on port 5678..."
    exec python3 -m debugpy --listen 0.0.0.0:5678 --wait-for-client \
        /usr/bin/odoo --config=/etc/odoo/odoo.conf "$@"
elif [ "$DEBUGPY" = "nowait" ]; then
    echo "===>Starting Odoo with debugpy (no wait) on port 5678..."
    exec python3 -m debugpy --listen 0.0.0.0:5678 \
        /usr/bin/odoo --config=/etc/odoo/odoo.conf "$@"
else
    echo "<---Starting Odoo normally...--->"
    exec /usr/bin/odoo --config=/etc/odoo/odoo.conf "$@"
fi
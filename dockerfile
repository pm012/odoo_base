FROM odoo:19.0

USER root
RUN pip install --no-cache-dir debugpy
USER odoo
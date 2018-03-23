FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

USER odoo

COPY partner_duplicate_mgmt /mnt/extra-addons/partner_duplicate_mgmt
COPY partner_multi_phone /mnt/extra-addons/partner_multi_phone

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

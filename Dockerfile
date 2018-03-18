FROM quay.io/numigi/odoo-public:11.0.1
MAINTAINER numigi <contact@numigi.com>

USER root

COPY ./docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./docker_files/odoo.conf /etc/odoo/odoo.conf

COPY ./partner_duplicate_mgmt /mnt/extra-addons/partner_duplicate_mgmt

EXPOSE 8069 8071
USER odoo

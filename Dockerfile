FROM quay.io/numigi/odoo-public:16.latest
LABEL maintainer="numigi <contact@numigi.com>"

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY contacts_config_menu_moved_right /mnt/extra-addons/contacts_config_menu_moved_right
COPY partner_autocomplete_disable /mnt/extra-addons/partner_autocomplete_disable
COPY partner_edit_group /mnt/extra-addons/partner_edit_group
COPY partner_firstname_before_lastname /mnt/extra-addons/partner_firstname_before_lastname
COPY partner_key_date /mnt/extra-addons/partner_key_date

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

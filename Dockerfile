FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install_all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY google_partner_address /mnt/extra-addons/google_partner_address
COPY partner_change_parent /mnt/extra-addons/partner_change_parent
COPY partner_duplicate_mgmt /mnt/extra-addons/partner_duplicate_mgmt
COPY partner_duplicate_multi_phone /mnt/extra-addons/partner_duplicate_multi_phone
COPY partner_duplicate_multi_relation /mnt/extra-addons/partner_duplicate_multi_relation
COPY partner_firstname_before_lastname /mnt/extra-addons/partner_firstname_before_lastname
COPY partner_key_date /mnt/extra-addons/partner_key_date
COPY partner_multi_phone /mnt/extra-addons/partner_multi_phone
COPY partner_multi_relation_work /mnt/extra-addons/partner_multi_relation_work
COPY partner_name_no_shortcut /mnt/extra-addons/partner_name_no_shortcut
COPY partner_unique_email /mnt/extra-addons/partner_unique_email
COPY partner_website_domain_only /mnt/extra-addons/partner_website_domain_only

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

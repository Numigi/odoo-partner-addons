FROM quay.io/numigi/odoo-public:12.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY contacts_config_menu_moved_right /mnt/extra-addons/contacts_config_menu_moved_right
COPY contacts_config_sale_manager /mnt/extra-addons/contacts_config_sale_manager
COPY google_partner_address /mnt/extra-addons/google_partner_address
COPY partner_change_parent /mnt/extra-addons/partner_change_parent
COPY partner_change_parent_affiliate /mnt/extra-addons/partner_change_parent_affiliate
COPY partner_contact_type_visible /mnt/extra-addons/partner_contact_type_visible
COPY partner_duplicate_mgmt /mnt/extra-addons/partner_duplicate_mgmt
COPY partner_duplicate_multi_phone /mnt/extra-addons/partner_duplicate_multi_phone
COPY partner_duplicate_multi_relation /mnt/extra-addons/partner_duplicate_multi_relation
COPY partner_edit_group /mnt/extra-addons/partner_edit_group
COPY partner_firstname_before_lastname /mnt/extra-addons/partner_firstname_before_lastname
COPY partner_gst_qst /mnt/extra-addons/partner_gst_qst
COPY partner_key_date /mnt/extra-addons/partner_key_date
COPY partner_multi_phone /mnt/extra-addons/partner_multi_phone
COPY partner_multi_relation_note /mnt/extra-addons/partner_multi_relation_note
COPY partner_multi_relation_strength /mnt/extra-addons/partner_multi_relation_strength
COPY partner_multi_relation_work /mnt/extra-addons/partner_multi_relation_work
COPY partner_name_no_shortcut /mnt/extra-addons/partner_name_no_shortcut
COPY partner_no_vat /mnt/extra-addons/partner_no_vat
COPY partner_no_vat_website_sale /mnt/extra-addons/partner_no_vat_website_sale
COPY partner_phone_no_envelope /mnt/extra-addons/partner_phone_no_envelope
COPY partner_phone_validation /mnt/extra-addons/partner_phone_validation
COPY partner_reference /mnt/extra-addons/partner_reference
COPY partner_unique_email /mnt/extra-addons/partner_unique_email
COPY partner_website_domain_only /mnt/extra-addons/partner_website_domain_only
COPY res_partner_bank_shared_account /mnt/extra-addons/res_partner_bank_shared_account

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo

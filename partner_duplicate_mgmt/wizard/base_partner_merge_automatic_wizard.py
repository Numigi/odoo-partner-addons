# © 2017 Savoir-faire Linux
# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from itertools import permutations
from odoo import _, api, models, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger('base.partner.merge')


def is_child_partner_of(partner_1, partner_2) -> bool:
    """Evaluate whether a given partner is a child of another partner.

    This function works recursively.
    It will return True if partner_1 is the grandchild of partner_2
    and so on.

    :param partner_1: the possible child partner
    :param partner_1: the possible parent partner
    """
    children = partner_1.with_context(active_test=False).search([
        ('parent_id', 'child_of', partner_2.id),
    ])
    return partner_1 in children


class MergePartnerAutomatic(models.TransientModel):

    _inherit = 'base.partner.merge.automatic.wizard'

    def _get_fk_on(self, table):
        """
        Ignore the table 'res_partner_duplicate' to avoid merging partner
        duplicates.
        """
        if ('merge_2_companies' in self.env.context):
            return []

        res = super(MergePartnerAutomatic, self)._get_fk_on(table)
        relations = [r for r in res if 'res_partner_duplicate' not in r[0]]
        return relations

    @api.model
    def _update_reference_fields(self, src_partners, dst_partner):
        """
        Override completely the original function to avoid merging messages
        and merge only attachments.
        """
        if src_partners.is_company and dst_partner.is_company:
            return

        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_id = %(dst_partner)s
            WHERE res_model = 'res.partner'
            AND res_id = %(src_partner)s
        """, {
            'dst_partner': dst_partner.id,
            'src_partner': src_partners.id,
        })

    def _update_children(self, src_partners, dst_partner):
        src_partners.child_ids.write({'parent_id': dst_partner.id})
        src_partners.write({
            'is_company': False,
            'parent_id': dst_partner.id,
        })

    def _check_partner_not_merged_with_parent(self, partners):
        for partner_1, partner_2 in permutations(partners, 2):
            if is_child_partner_of(partner_1, partner_2):
                raise ValidationError(_(
                    "You may not merge a partner ({child}) with its parent ({parent})."
                ).format(child=partner_1.display_name, parent=partner_2.display_name))

    def _merge(self, partner_ids, dst_partner, extra_checks=True):
        """
        Override completely the original function to remove useless code.
        """
        Partner = self.env['res.partner']
        partner_ids = Partner.browse(partner_ids).exists()

        self._check_partner_not_merged_with_parent(partner_ids)

        # remove dst_partner from partners to merge
        if dst_partner and dst_partner in partner_ids:
            src_partners = partner_ids - dst_partner
        else:
            ordered_partners = self._get_ordered_partner(partner_ids.ids)
            dst_partner = ordered_partners[-1]
            src_partners = ordered_partners[:-1]
        _logger.info("dst_partner: %s", dst_partner.id)

        # for contacts, check only users with enough rights can merge
        # contact with account moves
        if (
            not src_partners.is_company and not dst_partner.is_company and
            not self.env.user.has_group(
                'partner_duplicate_mgmt.group_contacts_merge_account_moves') and
            self.env['account.move'].sudo().search([
                ('partner_id', '=', src_partners.id)
            ])
        ):
            raise UserError(_(
                "You can not merge the contact %(contact)s because it is "
                "linked to journal entries. Please contact your "
                "administrator.") % {
                    'contact': src_partners.name
            })

        self._update_reference_fields(src_partners, dst_partner)

        # call sub methods to do the merge
        if src_partners.is_company and dst_partner.is_company:
            self.with_context({'merge_2_companies': True})\
                ._update_foreign_keys(src_partners, dst_partner)
            self._update_children(src_partners, dst_partner)
        else:
            self._update_foreign_keys(src_partners, dst_partner)

        _logger.info(
            '(uid = %s) merged the partners %r with %s',
            self._uid, src_partners.ids, dst_partner.id)

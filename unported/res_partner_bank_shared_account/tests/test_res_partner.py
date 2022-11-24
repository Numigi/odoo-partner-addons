# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import SavepointCase


class TestResPartnerBankSharedAccount(SavepointCase):

    def test_whenCreateSecondBankAccountWithSameNumber_thenAccountCreated(self):
        """
        Given a bank account exists with the number 1234
        When a second bank account is created with the same number 1234
        Then the both accounts have the same account number
        """
        partners = self.env['res.partner'].search([], limit=2)

        account_number = "1234"
        account_a = self.env['res.partner.bank'].create({
            "acc_number": account_number,
            "partner_id": partners[0].id,
        })

        account_b = self.env['res.partner.bank'].create({
            "acc_number": account_number,
            "partner_id": partners[1].id,
        })

        self.assertEqual(account_a.acc_number, account_b.acc_number)

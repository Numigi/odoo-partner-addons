# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import SavepointCase
from odoo import fields, SUPERUSER_ID
import time
from odoo.exceptions import Warning


class TestResPartnerBankSharedAccount(SavepointCase):

    def test_whenCreateSecondBankAccountWithSameNumber_thenAccountCreated(self):
        """
        Given a bank account exists with the number 1234
        When a second bank account is created with the same number 1234
        Then the both accounts have the same account number
        """
        account_number = "1234"
        account_a = self.env['res.partner.bank'].create({
            "acc_number": account_number
        })

        account_b = self.env['res.partner.bank'].create({
            "acc_number": account_number
        })

        self.assertEqual(account_a.acc_number, account_b.acc_number)


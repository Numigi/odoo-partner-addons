# © 2017 Savoir-faire Linux
# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestResPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'John Doe'})
        cls.organization_type = cls.env['res.partner.category'].create({
            'name': 'Supplier',
            'type': 'organization_type',
        })
        cls.profile = cls.env['res.partner.category'].create({
            'name': 'Python Development',
            'type': 'profile',
        })
        cls.personality = cls.env['res.partner.category'].create({
            'name': 'Friendly',
            'type': 'personality',
        })
        cls.personality_a = cls.env['res.partner.category'].create({
            'name': 'Professional',
            'type': 'personality',
        })
        cls.job_position = cls.env['res.partner.category'].create({
            'name': 'Developper',
            'type': 'job_position',
        })

    def test_organization_type_ids(self):
        self.partner.organization_type_ids = self.organization_type
        self.partner.refresh()
        self.assertEqual(self.partner.category_id, self.organization_type)

    def test_profile_ids(self):
        self.partner.profile_ids = self.profile
        self.partner.refresh()
        self.assertEqual(self.partner.category_id, self.profile)

    def test_personality_ids(self):
        self.partner.personality_ids = self.personality
        self.partner.refresh()
        self.assertEqual(self.partner.category_id, self.personality)

    def test_job_position_id(self):
        self.partner.job_position_id = self.job_position
        self.partner.refresh()
        self.assertEqual(self.partner.category_id, self.job_position)

    def test_all_fields_combined(self):
        self.partner.organization_type_ids = self.organization_type
        self.partner.profile_ids = self.profile
        self.partner.personality_ids = self.personality
        self.partner.job_position_id = self.job_position
        self.assertEqual(
            self.partner.category_id,
            self.organization_type | self.profile | self.personality | self.job_position)

    def test_all_fields_combined_on_create(self):
        partner = self.env['res.partner'].create({
            'name': 'Jane Doe',
            'organization_type_ids': [(4, self.organization_type.id)],
            'profile_ids': [(4, self.profile.id)],
            'personality_ids': [(4, self.personality.id)],
            'job_position_id': self.job_position.id,
        })
        self.assertEqual(
            partner.category_id,
            self.organization_type | self.profile | self.personality | self.job_position)

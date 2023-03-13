# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unidecode import unidecode
from odoo import api, models, fields
from odoo.osv.expression import AND

FULL_TEXT_FIELDS = {
    "email",
    "mobile",
    "name",
    "parent_id",
    "phone",
    "ref",
    "street",
    "street2",
}


class Partner(models.Model):

    _inherit = "res.partner"

    full_text = fields.Char()

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        ids = super()._name_search(name, args, operator, limit)
        res = self.browse(ids).sudo().name_get()

        positive_operators = ["=", "ilike", "=ilike", "like", "=like"]
        if operator not in positive_operators:
            return res

        if limit is None or len(res) < limit:
            remaining_limit = limit - len(res) if limit else None
            found_ids = [r[0] for r in res]
            args = AND([args or [], [("id", "not in", found_ids)]])
            partners = self._full_text_search(
                name, domain=args, limit=remaining_limit)
            res += [(p.id, p.display_name) for p in partners]

        return res

    @api.model
    def _search(self, args, *args_, **kwargs):
        domain = self._expand_full_text_domain(args)
        return super()._search(domain, *args_, **kwargs)

    def _full_text_search(self, name, domain=None, limit=None):
        full_text_domain = self._expand_full_text_domain(
            [("full_text", "like", name)])
        return self.search(AND([domain, full_text_domain]), limit=limit)

    def _expand_full_text_domain(self, domain):
        if not domain:
            domain = []

        def _iter_domain_leaves(domain):
            for leaf in domain:
                yield from _iter_leaves(leaf)

        def _iter_leaves(leaf):
            is_full_text_leaf = (
                isinstance(leaf, (tuple, list)) and
                len(leaf) == 3 and
                leaf[0] == "full_text"
            )
            if is_full_text_leaf:
                text = _normalize_text(leaf[2])
                terms = text.split(" ")
                yield from (("full_text", leaf[1], "%{}%".format(t)) for t in terms)
            else:
                yield leaf

        return list(_iter_domain_leaves(domain))

    @api.model_create_multi
    def create(self, vals):
        partners = super().create(vals)
        partners.update_full_text()
        return partners

    def write(self, vals):
        super().write(vals)
        if self._should_update_full_text(vals):
            self.update_full_text()
        return True

    def _should_update_full_text(self, vals):
        return FULL_TEXT_FIELDS.intersection(vals)

    def update_full_text(self):
        for partner in self:
            partner._update_full_text()

        children = self.mapped("child_ids")
        if children:
            children.update_full_text()

        return True

    def _update_full_text(self):
        self.full_text = self._get_full_text()

    def _get_full_text(self):
        terms = self._get_full_text_terms()
        terms = _get_terms_with_variants(terms)
        text = _normalize_text(" ".join(terms))
        words = set(text.split(" "))
        return " ".join(words)

    def _get_full_text_terms(self):
        return {
            self.display_name,
            self.phone or "",
            self.mobile or "",
            _normalize_phone_number(self.phone),
            _normalize_phone_number(self.mobile),
            self.email or "",
            self.street or "",
            self.street2 or "",
            self.ref or "",
        }


def _normalize_phone_number(phone):
    return (phone or "").replace(" ", "").replace("(", "").replace(")", "")


def _get_terms_with_variants(terms):
    res = list(terms)

    for term in terms:
        if "-" in term:
            res.append(term.replace("-", ""))

    return res


def _normalize_text(text):
    return unidecode(text).lower().replace(".", "").replace("-", " ")

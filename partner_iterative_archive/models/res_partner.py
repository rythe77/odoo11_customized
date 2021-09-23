from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def toggle_active(self):
        res = super().toggle_active()
        if self.env.context.get("skip_child_toggle_active"):
            return res
        for partner in self.filtered(lambda x: not x.active):
            partner.child_ids.filtered(lambda x: not x.active == x.parent_id.active).toggle_active()
        return res

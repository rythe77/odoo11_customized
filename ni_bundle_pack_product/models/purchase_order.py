from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_bundle_product_list(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Product Pack'),
                'res_model': 'bundle.wizard',
                'target': 'new',
                'view_id': self.env.ref('ni_bundle_pack_product.ni_bundle_wizard_view_form').id,
                'view_mode': 'form',
                'view_type': 'form',
                'context': {}
                }

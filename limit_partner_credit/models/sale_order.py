# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm_limited(self):
        for sale in self:
            credit = sale.partner_id.credit
            current_total = sale.amount_total
            credit_limit = sale.partner_id.credit_limit
            if credit_limit == 0:
                sale.action_confirm()
            elif credit + current_total > credit_limit:
                raise UserError(_('''Cannot confirm the quotation because the customer exceed the credit limit!\n
                                        This customer current credit is Rp %d, including the current quotation, the total is Rp %d.
                                        The credit limit is Rp %d.''') % (credit,current_total + credit,credit_limit))
            else:
                sale.action_confirm()
        return True
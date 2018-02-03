# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import re

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        invoice = self._context.get('invoice', False)
        self._post_validate()
        for move in self:
            move.line_ids.create_analytic_lines()
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id

                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                        match = re.sub(r'\d+$', '', new_name)
                        if match and invoice and invoice.picking_id:
                            new_name = match + invoice.picking_id.sequence_number_copy
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name
        return self.write({'state': 'posted'})
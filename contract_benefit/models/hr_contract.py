from odoo import api, fields, models, _

class Contract(models.Model):
    _inherit = 'hr.contract'

    benefit = fields.Monetary('Job Benefits', store=True, help="Employee's monthly benefits.")
    benefit_id = fields.Many2one('hr.benefit', string='Benefit Type', required=True, ondelete='cascade', index=True)
    level_id = fields.Many2one('hr.level', string='Level', required=True, ondelete='cascade', index=True)

    @api.onchange('benefit_id')
    def benefit_id_change(self):
        for benefit in self:
            benefit.benefit = benefit.benefit_id.amount

    @api.onchange('level_id')
    def level_id_change(self):
        for level in self:
            level.wage = level.level_id.amount

from odoo import models, fields, api

class ProductLabelWizard(models.TransientModel):
    """Wisaya Label Produk."""

    _name = 'product.label.wizard'
    _description = 'Wisaya Label Produk'

    qr_code = fields.Binary('QR Code')
    name = fields.Char('Name')
    default_code = fields.Char('Internal Reference')
    print_wizard = fields.Many2one('product.label.print.wizard')
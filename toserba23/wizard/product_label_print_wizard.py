from odoo import models, fields, api

class ProductLabelPrintWizard(models.TransientModel):
    """Wisaya Cetak Label Produk."""

    _name = 'product.label.print.wizard'
    _description = 'Wisaya Cetak Label Produk'

    number_of_copy = fields.Integer(string="Jumlah Rangkap", default=1)
    product_label_wizard = fields.One2many('product.label.wizard', 'print_wizard',
                                          string='Products')

    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        return self._export()

    def _prepare_data(self, product):
        self.ensure_one()
        return {
            'qr_code': product.qr_code,
            'default_code': product.default_code,
            'name': product.name,
            'print_wizard': self.id,
        }

    def _export(self):
        """Expor ke PDF."""
        products = self.env["product.template"].browse(self._context['active_ids'])
        for product in products:
            data = self._prepare_data(product)
            self.env['product.label.wizard'].create(data)
        return self.env.ref(
            'toserba23.report_product_label').report_action(
            self)
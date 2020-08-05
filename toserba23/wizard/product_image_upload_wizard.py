from odoo import api, fields, models, tools, _

class ProductImageUploadWizard(models.TransientModel):
    """Wisaya Upload Gambar Produk."""

    _name = 'product.image.upload.wizard'
    _description = 'Wisaya Upload Gambar Produk'

    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    description = fields.Text(
        'Description', translate=True,
        help="A precise description of the Product, used only for internal information purposes.")

    @api.model
    def default_get(self, fields):
        res = super(ProductImageUploadWizard, self).default_get(fields)
        product_ids = self.env.context.get('active_ids', [])
        if not product_ids:
            return res
        product_id = product_ids[0]

        product = self.env['product.template'].browse(product_id)

        res.update({'description': product.description})

        return res

    @api.multi
    def button_upload_image(self):
        self.ensure_one()
        return self._upload()

    def _upload(self):
        """Upload image."""
        data = {
            'image': self.image,
            'description': self.description,
        }

        products = self.env["product.template"].browse(self._context['active_ids'])
        products.ensure_one()
        for product in products:
            product.sudo().write(data)
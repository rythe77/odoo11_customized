# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round

class Product(models.Model):
    _inherit = 'product.template'

    #Modify existing fields
    responsible_id = fields.Many2one('res.users', string='Responsible', related='categ_id.responsible_id', default=lambda self: self.env.uid, required=True, readonly=True)
    list_price = fields.Float(
        'Sale Price', default=1.0, readonly=False, store=True,
        digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman",
        help="Base price to compute the customer price. Sometimes called the catalog price.")
    lst_price = fields.Float(
        'Public Price', related='list_price', groups="sales_team.group_sale_salesman",
        digits=dp.get_precision('Product Price'))

    #Create new custom fields
    x_harga_jual = fields.Float('Harga Jual', compute='_copy_pricelist', readonly=True, store=False, digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_grosir = fields.Float('Harga Grosir', compute='_copy_pricelist', readonly=True, store=False, digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_toko = fields.Float('Harga Toko', compute='_copy_pricelist', readonly=True, store=False,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_bulukumba = fields.Float('Harga Bulukumba', compute='_copy_pricelist', readonly=True, store=False,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_bulukumbas = fields.Float('Harga Bulukumba S', compute='_copy_pricelist', readonly=True, store=False,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_promo = fields.Float('Harga Promo', compute='_copy_pricelist', readonly=True, store=False,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_promo_cash = fields.Float('Promo Cash', compute='_copy_pricelist', readonly=True, store=False,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")

    #@api.depends('item_ids', 'list_price')
    @api.multi
    def _copy_pricelist(self):
        pricelists = self.env['product.pricelist'].search([])
        for pricelist in pricelists:
            if pricelist.name == 'Harga jual':
                jual_prices = pricelist.get_products_price(self, [1.0]*len(self), ['']*len(self))
            elif pricelist.name == 'Harga grosir':
                grosir_prices = pricelist.get_products_price(self, [1.0]*len(self), ['']*len(self))
            elif pricelist.name == 'Harga toko':
                toko_prices = pricelist.get_products_price(self, [1.0]*len(self), ['']*len(self))
            elif pricelist.name == 'Harga bulukumba':
                bulukumba_prices = pricelist.get_products_price(self, [1.0]*len(self), ['']*len(self))
            elif pricelist.name == 'Harga bulukumba s':
                bulukumbas_prices = pricelist.get_products_price(self, [1.0]*len(self), ['']*len(self))
            elif pricelist.name == 'Harga promo':
                promo_prices = pricelist.get_products_price(self, [10000.0]*len(self), ['']*len(self))
            elif pricelist.name == 'Promo cash':
                promocash_prices = pricelist.get_products_price(self, [10000.0] * len(self), [''] * len(self))
        # product = self.env['product.template'].browse(self._origin.id) if hasattr(self, '_origin') else self
        for record in self:
            vals = {}
            if jual_prices:
                vals['x_harga_jual'] = jual_prices.get(record.id, 0.0)
            if grosir_prices:
                vals['x_harga_grosir'] = grosir_prices.get(record.id, 0.0)
            if toko_prices:
                vals['x_harga_toko'] = toko_prices.get(record.id, 0.0)
            if bulukumba_prices:
                vals['x_harga_bulukumba'] = bulukumba_prices.get(record.id, 0.0)
            if bulukumbas_prices:
                vals['x_harga_bulukumbas'] = bulukumbas_prices.get(record.id, 0.0)
            if promo_prices:
                vals['x_harga_promo'] = promo_prices.get(record.id, 0.0)
            if promocash_prices:
                vals['x_promo_cash'] = promocash_prices.get(record.id, 0.0)
            record.update(vals)

    def action_view_stock_moves(self):
        """Update stock move button to show stock.move, not stock.move.line"""
        self.ensure_one()
        action = self.env.ref('stock.stock_move_action').read()[0]
        action['domain'] = [('product_id.product_tmpl_id', 'in', self.ids)]
        return action


class ProductProductInherited(models.Model):
    _inherit = 'product.product'

    # Create new custom fields
    x_qty_available_0 = fields.Float(
        'Quantity On Hand', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Current quantity of products in stock location 0.\n")
    x_virtual_available_0 = fields.Float(
        'Forecast Quantity', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Forecast quantity (computed as Quantity On Hand "
             "- Outgoing + Incoming) in stock location 0\n")
    x_incoming_qty_0 = fields.Float(
        'Incoming', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity of products that are planned to arrive.\n")
    x_outgoing_qty_0 = fields.Float(
        'Outgoing', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity of products that are planned to leave.\n")

    x_qty_available_1 = fields.Float(
        'Quantity On Hand', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Current quantity of products in stock location 1.\n")
    x_virtual_available_1 = fields.Float(
        'Forecast Quantity', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Forecast quantity (computed as Quantity On Hand "
             "- Outgoing + Incoming) in stock location 1\n")
    x_incoming_qty_1 = fields.Float(
        'Incoming', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity of products that are planned to arrive.\n")
    x_outgoing_qty_1 = fields.Float(
        'Outgoing', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
       help="Quantity of products that are planned to leave.\n")

    x_qty_available_99 = fields.Float(
        'Quantity On Hand', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Current quantity of products in stock location 1.\n")
    x_qty_available_98 = fields.Float(
        'Quantity On Hand', compute='_compute_quantities_loc_pref',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Current quantity of products in stock location 0.\n")

    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_quantities_loc_pref(self):
        for product in self:
            ckl_location = self.env['stock.location'].search([('name', '=', 'Cakalang')], limit=1)
            if ckl_location:
                ckl_location_id = ckl_location.id
                product.x_qty_available_0 = product.with_context({'location' : ckl_location_id}).qty_available
                product.x_virtual_available_0 = product.with_context({'location' : ckl_location_id}).virtual_available
                product.x_incoming_qty_0 = product.with_context({'location' : ckl_location_id}).incoming_qty
                product.x_outgoing_qty_0 = product.with_context({'location' : ckl_location_id}).outgoing_qty

            prl_location = self.env['stock.location'].search([('name', '=', 'Parangloe')], limit=1)
            if prl_location:
                prl_location_id = prl_location.id
                product.x_qty_available_1 = product.with_context({'location' : prl_location_id}).qty_available
                product.x_virtual_available_1 = product.with_context({'location' : prl_location_id}).virtual_available
                product.x_incoming_qty_1 = product.with_context({'location' : prl_location_id}).incoming_qty
                product.x_outgoing_qty_1 = product.with_context({'location' : prl_location_id}).outgoing_qty
            
            bs_location = self.env['stock.location'].search([('name', '=', 'BarangBS-PRL')], limit=1)
            if bs_location:
                bs_location_id = bs_location.id
                product.x_qty_available_99 = product.with_context({'location' : bs_location_id}).qty_available
            bs_ckl_location = self.env['stock.location'].search([('name', '=', 'BarangBS-CKL')], limit=1)
            if bs_ckl_location:
                bs_ckl_location_id = bs_ckl_location.id
                product.x_qty_available_98 = product.with_context({'location' : bs_ckl_location_id}).qty_available
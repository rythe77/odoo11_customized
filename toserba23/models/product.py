# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round

class Product(models.Model):
    _inherit = 'product.template'

    #Modify existing fields
    list_price = fields.Float(
        'Sale Price', default=1.0, compute='_copy_pricelist', readonly=True, store=True,
        digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman",
        help="Base price to compute the customer price. Sometimes called the catalog price.")
    lst_price = fields.Float(
        'Public Price', related='list_price', groups="sales_team.group_sale_salesman",
        digits=dp.get_precision('Product Price'))

    #Create new custom fields
    x_harga_grosir = fields.Float('Harga Grosir', compute='_copy_pricelist', readonly=True, store=True, digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_toko = fields.Float('Harga Toko', compute='_copy_pricelist', readonly=True, store=True,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_bulukumba = fields.Float('Harga Bulukumba', compute='_copy_pricelist', readonly=True, store=True,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_harga_promo = fields.Float('Harga Promo', compute='_copy_pricelist', readonly=True, store=True,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")
    x_promo_cash = fields.Float('Promo Cash', compute='_copy_pricelist', readonly=True, store=True,  digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")

    @api.depends('item_ids')
    def _copy_pricelist(self):
        for record in self:
            list_price_min=10000
            x_harga_grosir_min=10000
            x_harga_toko_min=10000
            x_harga_bulukumba_min=10000
            x_harga_promo_min=10000
            x_promo_cash_min=10000
            for item in record.item_ids:
                if item.pricelist_id.name=="Harga jual" and item.min_quantity<list_price_min:
                    record.list_price = item.fixed_price
                    list_price_min=item.min_quantity
                if item.pricelist_id.name=="Harga grosir" and item.min_quantity<x_harga_grosir_min:
                    record.x_harga_grosir = item.fixed_price
                    x_harga_grosir_min=item.min_quantity
                if item.pricelist_id.name=="Harga toko" and item.min_quantity<x_harga_toko_min:
                    record.x_harga_toko = item.fixed_price
                    x_harga_toko_min=item.min_quantity
                if item.pricelist_id.name=="Harga bulukumba" and item.min_quantity<x_harga_bulukumba_min:
                    record.x_harga_bulukumba = item.fixed_price
                    x_harga_bulukumba_min=item.min_quantity
                if item.pricelist_id.name=="Harga promo" and item.min_quantity<x_harga_promo_min:
                    record.x_harga_promo = item.fixed_price
                    x_harga_promo_min=item.min_quantity
                if item.pricelist_id.name=="Promo cash" and item.min_quantity<x_promo_cash_min:
                    record.x_promo_cash = item.fixed_price
                    x_promo_cash_min=item.min_quantity


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
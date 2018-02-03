# -*- coding: utf-8 -*-
{
    'name': "contact_transporter",

    'summary': """
        Add transporter checkbox from contact list, and add transporter field to SO""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Warehouse',
    'version': '1.0',

    'depends': ['base','sale','stock','sale_stock'],

    'data': [
        #'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
{
    'name': "delivery_invoice_same_sequence",

    'summary': """
        Invoice will use the same sequence number as its picking""",

    'description': """
        Required: deliver_auto_invoice. This is needed in order to
        ensure a one-on-one relationship between picking and invoice
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Stock',
    'version': '1.0',

    'depends': ['base','deliver_auto_invoice'],

    'data': [
        #'security/ir.model.access.csv',
        'views/stock_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
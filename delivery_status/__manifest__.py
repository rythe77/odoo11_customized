# -*- coding: utf-8 -*-
{
    'name': "delivery_status",

    'summary': """
        Show delivery status on SO""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Sales',
    'version': '1.0',

    'depends': ['base','sale','sale_stock'],

    'data': [
        #'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/purchase_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
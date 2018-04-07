# -*- coding: utf-8 -*-
{
    'name': "limit_partner_credit",

    'summary': """
        Block quotation confirmation into SO if the partner exceed their credit limit""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['base', 'sale', 'account'],

    'data': [
        #'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
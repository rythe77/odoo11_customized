# -*- coding: utf-8 -*-
{
    'name': "discount_total_sale",

    'summary': """
        Add discount field on total sales of SO and Invoice""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Sales',
    'version': '1.0',

    'depends': ['base','sale','account','indonesia_template'],

    'data': [
        #'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/account_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
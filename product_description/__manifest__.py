# -*- coding: utf-8 -*-
{
    'name': "product_description",

    'summary': """
        Add product description into sale order lines,
        which then transferred to lines in delivery order when confirmed""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Sales',
    'version': '1.0',

    'depends': ['base','sale','sale_stock','stock'],

    'data': [
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
{
    'name': "sale_requested_date",

    'summary': """
        Add requested date on sales order which is automatically transferred to delivery order""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Sales',
    'version': '1.0',

    'depends': ['base','sale','sale_stock'],

    'data': [
        'views/sale_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
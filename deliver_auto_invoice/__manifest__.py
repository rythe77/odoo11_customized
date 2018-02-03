# -*- coding: utf-8 -*-
{
    'name': "deliver_auto_invoice",

    'summary': """
        Automatically invoice done delivery""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Account',
    'version': '1.0',

    'depends': ['base','sale','sale_stock','stock','stock_account','account'],

    'data': [
        #'security/ir.model.access.csv',
        #'security/auto_validate.xml',
        'views/stock_view.xml',
        'views/res_config_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
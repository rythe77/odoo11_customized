# -*- coding: utf-8 -*-
{
    'name': "equity_change",

    'summary': """
        Allow input of equity nominal change""",

    'description': """
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Accounting',
    'version': '1.0',

    'depends': ['base', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'views/equity_holder_view.xml',
        'wizard/equity_change_register_payment.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
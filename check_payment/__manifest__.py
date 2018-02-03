# -*- coding: utf-8 -*-
{
    'name': "check_payment",

    'summary': """
        Manage check/giro payment on accounting module""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Accounting',
    'version': '1.0',

    'depends': ['base','account'],

    'data': [
        'views/account_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
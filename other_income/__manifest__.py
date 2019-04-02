# -*- coding: utf-8 -*-
{
    'name': "other_income",

    'summary': """
        Allow input of other income""",

    'description': """
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Accounting',
    'version': '1.0',

    'depends': ['base', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'views/other_income_view.xml',
        'wizard/other_income_register_payment.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
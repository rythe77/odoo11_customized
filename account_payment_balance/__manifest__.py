# -*- coding: utf-8 -*-
{
    'name': "account_payment_balance",

    'summary': """
        Show unapplied balance of payment""",

    'description': """
        For Odoo Version 11.0, this module shows the unapplied balance of Payments on the list and form view, with a filter to show payments with a positive unapplied balance.
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Accounting',
    'version': '1.0',

    'depends': ['base','account'],

    'data': [
        'views/account_payment.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
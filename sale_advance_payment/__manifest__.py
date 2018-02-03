# -*- coding: utf-8 -*-
{
    'name': "sale_advance_payment",

    'summary': """
        Allow to add advance payments on sales and then use it on invoices""",

    'description': """
        List of modified items:
            - Enable advance payment, even when SO status is still quotation
            - Link SO with payments during advance payment
            - Show advance payment amount in the tree and form view of SO
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Sales',
    'version': '1.0',

    'depends': ['base','sale','account'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/sale_advance_payment_wzd_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
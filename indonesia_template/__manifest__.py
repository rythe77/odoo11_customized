# -*- coding: utf-8 -*-
{
    'name': "indonesia_template",

    'summary': """
        Starter template for company start using Odoo in Indonesia""",

    'description': """
        List of modified items:
            - Sale main menu: no invoicing
            - Sale order print: no proforma
            - Custom SO form and search view
            - Custom DO form and search view
            - Custom Invoice form and search view
            - Hide original report
            - Disable delete button on form view of SO, DO, and cust invoice
            - Clean external layout template
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.5',

    'depends': ['base','sale','sale_stock','stock','account'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/account_view.xml',
        'views/hide_batch_invoice_button.xml',
        'reports/hide_original_report.xml',
        'reports/template_layout.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
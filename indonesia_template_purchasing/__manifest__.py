# -*- coding: utf-8 -*-
{
    'name': "indonesia_template_purchasing",

    'summary': """
        Starter template for company start using Odoo in Indonesia""",

    'description': """
        List of modified items:
            - Custom PO form and search view
            - Disable delete button on form view of PO
            - Sale main menu: no invoicing
            - Sale order print: no proforma
            - Hide original report
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.5',

    'depends': ['base', 'purchase', 'indonesia_template'],

    'data': [
        #'security/ir.model.access.csv',
        'views/purchase_view.xml',
        'reports/hide_original_report.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
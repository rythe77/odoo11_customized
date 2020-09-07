# -*- coding: utf-8 -*-
{
    'name': "toserba23_branch",

    'summary': """
        Odoo customization for Toserba 23 branch office""",

    'description': """
        List of modified items:
            -
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base', 'sale', 'stock', 'account', 'purchase', 'sale_margin', 'hr_expense', 'hr_payroll', 'stock_account'
                ],

    'data': [
        'security/security.xml',
        #'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/purchase_view.xml',
        'views/hr_view.xml',
        'reports/master_template.xml',
        'reports/saleorder_document.xml',
        'reports/picking_document.xml',
        'reports/delivery_document.xml',
        'reports/delivery_document_copy.xml',
        'reports/pick_delivery_set_document.xml',
        'reports/invoice_document.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}

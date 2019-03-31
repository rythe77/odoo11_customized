# -*- coding: utf-8 -*-
{
    'name': "rejeki_jaya",

    'summary': """
        Modifikasi Odoo sesuai permintaan Rejeki Jaya""",

    'description': """
        Yang dimodifikasi:
            -
        Todo:
            - Tampilan data master produk secara default sebaiknya tampilan daftar
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base', 'hr_payroll', 'hr_attendance',
        'contract_benefit',
        'web_m2x_options',
        'indonesia_template',
        'indonesia_template_purchasing',
        'reset_sequence_monthly',
        'product_description',
        'hide_confidential_info',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_view.xml',
        'views/hr_menu.xml',
        'views/hr_fine_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
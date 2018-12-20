# -*- coding: utf-8 -*-
{
    'name': "attendances_based_payroll",

    'summary': """
        Modified payroll working time/days to suit Toserba 23""",

    'description': """
        List of modified items:
            -
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Human Resources',
    'version': '1.0',

    'depends': ['base', 'hr_attendance', 'hr_payroll', 'hr_payroll_payment'],

    'data': [
        #'security/ir.model.access.csv',
        'views/hr_view.xml',
        'views/hr_menu.xml',
        'views/hr_fine_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
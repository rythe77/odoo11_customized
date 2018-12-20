# -*- coding: utf-8 -*-
{
    'name': "Employee QR Code",

    'summary': """
        Creates QR Code for Employees and can be used for Employee Tag and other scanning purposes.""",
    'description': """
        Creates QR Code for Employees and can be used for Employee Tag and other scanning purposes.
    """,
    'author': "Ryanto The",
    'website': "",

    'category': 'HR',
    'version': '1.0',

    'depends': ['base', 'hr', 'hr_attendance', 'indonesia_template'],
    'data': [
        'views/views.xml',
        'reports/employee_tag_document.xml',
    ],
    'installable': True,
}
# -*- coding: utf-8 -*-
{
    'name': "androidapp_companion",

    'summary': """
        Companion module to be used with custom Android App for Toserba23""",

    'description': """
        List of modified items:
            - app version check on res company, and also provide banner message for app
            - hr.holidays write and create method overwrite
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['base', 'hr', 'hr_holidays'],

    'data': [
        'security/ir.model.access.csv',
        'views/app_view.xml'
    ],
}
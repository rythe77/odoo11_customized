# -*- coding: utf-8 -*-
{
    'name': "contract_benefit",

    'summary': """
        Add benefits line to employee contract, and modify it to conform to Toserba 23 payroll structure""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Human Resources',
    'version': '1.0',

    'depends': ['base', 'hr_contract'],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/hr_benefit_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
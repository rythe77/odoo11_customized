# -*- coding: utf-8 -*-
{
    'name': "hide_confidential_info",

    'summary': """
        Enable hiding certain confidential info""",

    'description': """
        List of hideable items:
            - Product cost price
            - Partner detail
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': ['base','sale','account'],

    'data': [
        'security/view_cost_price.xml',
        'security/view_partner_detail.xml',
        'views/hide_product_cost.xml',
        'views/hide_partner_detail.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
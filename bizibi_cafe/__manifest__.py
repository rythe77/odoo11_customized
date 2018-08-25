# -*- coding: utf-8 -*-
{
    'name': "bizibi_cafe",

    'summary': """
        Modify Odoo to suit Bizibi Cafe""",

    'description': """
        List of modified items:
            - Custom POS ticket
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'POS',
    'version': '1.0',

    'depends': ['base', 'point_of_sale', 'pos_restaurant'],

    'data': [
        #'security/ir.model.access.csv',
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/pos.xml',
             'static/src/xml/pos_restaurant.xml',
             ],
    'demo': [
        #'demo/demo.xml',
    ],
}
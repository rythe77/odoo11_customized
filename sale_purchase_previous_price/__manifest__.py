# -*- coding: utf-8 -*-
{
    'name': "sale_purchase_previous_price",

    'summary': """
        Show past sale/purchase for the partner in a SO form view""",

    'description': """
        Add a button on SO form view, which will show past sale/purchase in tree view
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Sales',
    'version': '0.1',

    'depends': ['base', 'sale', 'purchase'],

    'data': [
        #'security/ir.model.access.csv',
        'views/view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
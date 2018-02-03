# -*- coding: utf-8 -*-
{
    'name': "petstore",
    'summary': 'Sell pet toys',
    'description':
        """
OpenERP Pet Store
=================

A wonderful application to sell pet toys.
        """,
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'sale_stock',
    ],

    'data': [
        "views/petstore.xml",
        "views/petstore_data.xml",
        "oepetstore.message_of_the_day.csv",
    ],

    'qweb': ['static/src/xml/*.xml'],
    'application': True,
}
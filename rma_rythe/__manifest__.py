# -*- coding: utf-8 -*-
{
    'name': "rma_rythe",

    'summary': """
        Module for managing RMA (Return merchandise authorization)""",

    'description': """
        RMA (Return merchandise authorization) is a part of the process to receiving a refund,
        replacement or repair of purchased items by customers from vendors / distributors / retailers.
        Many retailers will accept returns from customer under certain conditions which are described
        in their return policies, based on that either retailer will approve or reject a request for return.
        
        Key Features:
            - Allows users to create predefined Return reason & set appropriate Action to be taken.
            - Allows users to Approve or Reject an RMA Request from Customer.
            - Allow users to manage return or replacement in Odoo.
            - User can take actions like Refund, Replacement or Repair in Odoo.
            - Product return which mark a non-damaged will be returned to warehouse location, not rma location
            - RMA for Odoo App generate documents automatically such as Delivery Order / Credit Note based on action taken by responsible person.
            - Allow users to see all the documents from the same screen.
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Sales',
    'version': '1.0',

    'depends': ['base', 'stock', 'account'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/rma_data.xml',
        'wizards/rmain_send_wizard.xml',
        'wizards/rmain_int_transfer_wizard.xml',
        'wizards/rmaout_create_wizard.xml',
        'wizards/rmaout_receive_wizard.xml',
        'views/rma_menu_view.xml',
        'views/rmaout_menu_view.xml',
        'views/stock_warehouse.xml',
        'views/stock_view.xml',
        'views/invoice_view.xml',
        'wizards/rma_product_replacement.xml',
        'wizards/rma_service_product.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
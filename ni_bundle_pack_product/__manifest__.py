{
    'name': "Odoo Product Pack (Bundle) or Combo Products",
    'summary': """Bundle Pack Product""",
    'description': """
Bundle Pack Product 
""",
    "category":  "Sales",
    "version":  "11.0.1.0",
    "images": ['static/description/Banner.gif'],
    "author":  "Nevioo Technologies",
    "license": 'OPL-1',
    'depends': ['base', "product", "sale_management", "purchase", "stock"],
    'data': [
        'security/ir.model.access.csv',
        'wizard/view_bundle_wizard.xml',
        'views/view_product_template.xml',
        'views/view_bundle_product.xml',
        'views/view_sale_order.xml',
        'views/view_purchase_order.xml',
        'views/res_config_view.xml',
    ],
    'qweb': [],
}
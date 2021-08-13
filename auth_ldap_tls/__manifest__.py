# -*- coding: utf-8 -*-
{
    'name': "auth_ldap_tls",

    'summary': """
        Fixed Odoo LDAP authentication when using StartTLS""",

    'author': "Ryanto The",
    'website': "",

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': ['base', 'auth_ldap'],

    'data': [
        'views/ldap_installer_view.xml',
    ],
}

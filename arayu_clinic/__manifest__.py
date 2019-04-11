# -*- coding: utf-8 -*-
{
    'name': "arayu_clinic",

    'summary': """
        Modifikasi Odoo sesuai permintaan Arayu Aesthetic Clinic""",

    'description': """
        Daftar perubahan:
            - Layout cetak faktur custom
        Pengaturan awal:
            - Aktifkan mata uang IDR dan nonaktifkan yang lainnya
            - Input data perusahaan
            - Buat pengguna baru
            - Set default tz dan notif ketika buat pengguna baru
            - Set decimal precision, price:0; product uom:2; diskon:1
            - Set format kertas thermal printer 150x80mm, Tegak: allside 4
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','account',
    ],

    'data': [
        'security/ir.model.access.csv',
        'reports/invoice_document.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
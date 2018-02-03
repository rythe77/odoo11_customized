# -*- coding: utf-8 -*-
{
    'name': "asia_florist",

    'summary': """
        Modifikasi Odoo sesuai permintaan Asia Florist""",

    'description': """
        Yang dimodifikasi:
            - Field2 custom dari sales order, delivery order, dan faktur
            - Custom form dan tree view untuk sales order, delivery order, dan faktur
            - Keterangan khusus untuk produk di SO dan DO
            - Kontak detail pelanggan tidak boleh diakses oleh pegawai
            - Bayar uang muka sebelum sales order dikonfirmasi
            - Input tanggal pengiriman di SO
            - Menu simpel untuk DO dan akuntansi
            - Filter tampilan SO menurut tanggal pesan dan pengiriman
            - Filter tampilan DO menurut tanggal pengiriman
            - Sederhanakan tampilan form pelanggan
            - Sederhanakan tampilan form produk
            - Atur hak akses untuk masing2 tombol tampilan formulir
            - Format print Surat Jalan
            - Format print Faktur
            - Format print Kuitansi
            - Rekapan harian SO
        Todo:
        Not Todo:
            - Fitur cari pelanggan melalui nomor telpon
            - Fitur tampilan lunas tidak lunas di SO
        Pengaturan awal:
            - Hapus default taxes dari pengaturan penagihan
            - Aktifkan mata uang IDR dan nonaktifkan yang lainnya
            - Input data perusahaan
            - Buat pengguna baru
            - Set default tz dan notif ketika buat pengguna baru
            - Set decimal precision
            - Set saluran penjualan
            - Set format kertas laporan; Portrait: mb10, mt32, hs27; Landscape: mb10, kuitansi : mside:15mm,mt mb hs normal
                rekap SO: all side 7 hs 0, A4 landscape
            - Add system parameters so that report can work correctly (key:report.url; value:http://localhost:8069)
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Localized',
    'version': '0.8',

    'depends': [
        'base','sale','stock','account',
        'backend_theme_v11',
        'login_user_detail',
        'total_payable_receivable',
        'web_disable_export_delete_button',
        'indonesia_template',
        'sale_requested_date',
        'sale_advance_payment',
        'product_description',
        'hide_confidential_info',
        'reset_sequence_monthly',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'reports/saleorder_summary.xml',
        'reports/delivery_document.xml',
        'reports/invoice_document.xml',
        'reports/payment_document.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/account_view.xml',
        'views/partner_view.xml',
        'views/product_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
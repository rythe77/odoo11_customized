# -*- coding: utf-8 -*-
{
    'name': "bintang_satelit",

    'summary': """
        Modifikasi Odoo sesuai permintaan Bintang Satelit Makassar""",

    'description': """
        Yang dimodifikasi:
            - Sistem diskon di total jumlah
            - Input tanggal pengiriman di SO
            - Keterangan khusus untuk produk di SO dan DO
            - Kontak detail pelanggan dan modal hanya bisa diakses oleh orang tertentu
            - Faktur otomatis dibuat waktu surat jalan divalidasi
            - Faktur penjualan dan refund penjualan nomornya sama dengan surat jalan
            - Field2 custom dan tampilan dari purchase order, sales order, delivery order, dan faktur
            - Custom sale order, delivery slip, and invoices report
            - Penomoran direset tiap bulan
        Todo:
            - Set penjualan konsinyasi
        Not Todo:
            - Cetak dokumen dikontrol hanya bisa 1x
            - Sistem diskon tambahannya dan tampilannya di faktur
        Pengaturan awal:
            - Hapus default taxes dari pengaturan penagihan
            - Aktifkan mata uang IDR dan nonaktifkan yang lainnya
            - Input data perusahaan
            - Buat pengguna baru
            - Set default tz dan notif ketika buat pengguna baru
            - Set decimal precision, diskon 3 digits, product qty 0 digit
            - Set saluran penjualan
            - Set format kertas laporan; Landscape: all-side margin: 7, hs:7
            - Add system parameters so that report can work correctly (key:report.url; value:http://localhost:8069)
            - Cek jurnal penjualan dan pembelian supaya faktur retur beda penomorannya
            - Set penomoran dokumen
            - Setup delivery type yang berbeda untuk barang retur
            - Set kategori produk untuk otomatis rekam ayat jurnal untuk pergerakan barang
            - Cek auto invoice validation
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Localized',
    'version': '0.2',

    'depends': [
        'base','sale','stock','account','purchase',
        'backend_theme_v11',
        'web_disable_export_delete_button',
        'indonesia_template',
        'indonesia_template_purchasing',
        'reset_sequence_monthly',
        'deliver_auto_invoice',
        'delivery_invoice_same_sequence',
        'sale_requested_date',
        'product_description',
        'hide_confidential_info',
        'discount_total_sale',
    ],

    'data': [
        #'security/ir.model.access.csv',
        'security/security.xml',
        'reports/sale_order_document.xml',
        'reports/delivery_document.xml',
        'reports/invoice_document.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/stock_view.xml',
        'views/account_view.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
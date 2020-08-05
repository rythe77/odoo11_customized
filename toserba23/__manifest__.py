# -*- coding: utf-8 -*-
{
    'name': "toserba23",

    'summary': """
        Modifikasi Odoo sesuai permintaan Toserba 23""",

    'description': """
        Yang dimodifikasi:
            - Login pengguna detail
            - Payable/Receivable di halaman detail rekanan
            - Penomoran direset tiap bulan
            - Input tanggal pengiriman di SO
            - Keterangan khusus untuk produk di SO dan DO
            - Kontak detail pelanggan dan modal hanya bisa diakses oleh orang tertentu
            - Faktur otomatis dibuat waktu surat jalan divalidasi
            - Tambahkan status pengiriman di SO
            - Tambahkan kolom diskon di PO
            - Tambahkan input ekspedisi di SO, PO, dan DO
            - Tambah langkah validasi untuk transfer barang
            - Manage pembayaran cek/giro
            - Kustomisasi akses keamanan sistem
            - Field2 custom dari sales order, delivery order, dan faktur
            - Custom form dan tree view untuk sales order, delivery order, dan faktur
            - Atur hak akses untuk masing2 tombol tampilan formulir
            - Kustomisasi dokumen SO, DO & Picking, Invoice, & Stock Inventry
            - Sistem absensi dan gaji kustom toserba 23
            - Kustomisasi dokumen katalog produk
            - Lock price unit edit based on groups and also limit pricelist option for that group
            - Partner summary report for use by marketing department
            - Separate groups access for purchasing in account module, also setup view only groups access
            - Add credit limit for customer
            - Stock inventory for a category also include sub category
            - Kustomisasi dokumen koreksi persediaan
            - Kustomisasi dokumen slip gaji
            - Kustomisasi dokumen transfer massal BS
            - Product purchase price and start date automatically updated when purchase order is confirmed
            - DO validation for stock user should be allowed, when qty done is equal to or less than qty todo
            - Tunjangan jabatan diatur di kontrak
            - Akses LIHAT absensi untuk petugas penggajian
            - Automatic email and sms system
            - Sistem daftar harga lebih kompleks
            - Upload product image
            - Sistem pencatatan tindakan indisipliner
            - Employee insurance module
            - Sistem cuti
        Todo:
            - nota tanggal lama tidak boleh edit penambahan barang
            - alert sistem ketika konfirmasi penjualan, jika ada nota yang jatuh tempo
            - data siapa pembuat SO di faktur pelanggan
            - Operasi Pembuangan dihilangkan dari akun kepala gudang
            - History edit data pelanggan
            - purchase price auto update mess, update also old price. Tikar jali M 140
            - Admin sales : edit data pelanggan. Sup Sales : + ubah naik harga. Sales Man : + perbaiki SO jd penawaran, ubah limit kredit dan lamanya.
            - Purchase request module, only to socialize and install in server
            - Employee orientation module, only to socialize and install in server
            - odoo user, employee, and partner mess
            - Handle mailing and thread so partner doesn't learn insider information
            - allow salesman to upload customer front shop photo to odoo from applicatoin
            - Attendance monthly report for all employee
            - Advance expense amount system
            - Expense stockable product for internal use
            - Notification for employee contract
            - Konfirmasi slip gaji massal
            - sistem pencatatan yang mirip seperti tindakan indisipliner untuk pelanggan
            - error access rule utk sales
            - integrasi google map ke data kontak
            - sistem pencatatan kunjungan sales menurut google map, https://apps.odoo.com/apps/modules/12.0/employee_tracking_log/
            - tanggal jatuh tempo faktur mau otomatis dimunculkan ketika pembuatan faktur
            - bonus prestasi karyawan menurut KPI
            - kunci SO yang sudah konfir
            - history perubahan data pelanggan
            - featured product view
            - real-time inventory correction system
            - Automatic wa notification system
            - Dasbor penagihan sebaiknya tampilkan jumlah yang belum dibayar, bukan jumlah total
            - Nisa mau dibatasi ubah harga di faktur
            - pembayaran di muka untuk pembelian
            - pak ilham tidak bisa lihat stok pada tanggal tertentu
            - sari selesaikan dokumen transfer untuk diantar belakangan, tapi tanggalnya selalu ikut tanggal selesai
            - pas simpan transfer barang, tanggal terjadwal & prioritas otomatis berubah kembali ke default
            - Tanggal terjadwal di DO susah tersimpan
            - Supervisor bisa tambah produk, khusus nama produk dan kodenya
            - Super call on method, should not list "administrator" as the document creator
            - Sistem hutang karyawan ke perusahaan
        Not Todo:
            - sales commission system
            - Sales group automatically fills in based on customer
            - Customize tree view column width
            - stock user can do backorder
            - automatic backorder
            - (???) show product qty on SO drop down list:
                https://www.odoo.com/forum/help-1/question/grid-like-multi-column-dropdown-selection-109295
            - (???) prevent horizontal scroll from disappearing
            - Paket print nota : 1 SO dan 2 Surat jalan
            - Run server_time_correction.reg on server windows computer to correct time
            - Create x_call_freq on res.partner field manually
            - Sistem pencatatan kunjungan sales
            - Problem with DO partner domain (problem only for odoo 10)
        Pengaturan awal:
            - Hapus default taxes dari pengaturan penagihan
            - Aktifkan mata uang IDR dan nonaktifkan yang lainnya
            - Input data perusahaan
            - Buat pengguna baru
            - Set default tz dan notif ketika buat pengguna baru
            - Set decimal precision
            - Set saluran penjualan
            - Set format kertas laporan A5 Landscape: allside 7, Katalog Produk: allside 12
            - Add system parameters so that report can work correctly (key:report.url; value:http://localhost:8069)
            - Sales settings: "Satuan", "Diskon", "Daftar Harga", "Margin", "Syarat & Ketentuan Standar", "Penagihan: yang dikirim", "Rute Order Spesifik"
            - Purchases settings: 
            - Inventory settings: "Banyak Gudang", "Rute Banyak Langkah"
            - Accounting settings:
            - Penggajian settings:
            - Karyawan settings:
            - Absensi settings: "PIN Karyawan"
            - Create warehouse: Internal Location for physical warehouse, transit location with no parent for BS and service goods
            - Sales Pricelist: Create manually; Sales Channel: Create manually
            - Delete UOM : lb(s), t, oz(s), cm, km, inch(es), foot(ft), mile(s), gal(s), fl oz, qt
            - Create bank and link it to journal account
            - Import excel : penomoran
            - Import excel : Chart of Account
            - Set Chart of Account in "Product Category: PDA, SIA, SOA, SVA"
        After module installation:
            - Import payment term
            - Import Partner
            - Import Product Category
            - Import UoM
            - Import Products
            - Import Koreksi persediaan for qty on hand
            - Import Reordering Rules
            - Create new menu; Add menu to additional feature group
            - Import Daftar Harga -> "Harga ecer", "Harga grosir", "Harga toko", "Harga bulukumba", "Harga promo", "Promo cash"
            - Run pull rules on sales order line for Cakalang warehouse --> tested!! Only need implementation on server database
            - Input employee data
            - Setup struktur gaji
            - Input employee contract
    """,

    'author': "Ryanto The",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base','mail','sale','stock','account','purchase','sale_margin','hr_expense', 'hr_payroll', 'crm', 'stock_account',
        #'backend_theme_v11',
        #'login_user_detail',
        #'web_disable_export_delete_button',
        #'total_payable_receivable',
        'web_m2x_options',
        'restrict_saleprice_change',
        'employee_qr_code',
        'hr_payroll_payment',
        'indonesia_template',
        'indonesia_template_purchasing',
        'reset_sequence_monthly',
        'deliver_auto_invoice',
        'sale_requested_date',
        'delivery_status',
        'product_description',
        'hide_confidential_info',
        'contact_transporter',
        'stock_picking_validation',
        'check_payment',
        'attendances_based_payroll',
        'limit_partner_credit',
        'stock_inventory_subcateg',
        'sale_advance_payment',
        'sale_purchase_previous_price',
        'equity_change',
        'rma_rythe',
        'contract_benefit',
        'other_income',
        'sms_frame',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/sale_margin_view.xml',
        'views/purchase_view.xml',
        'views/stock_view.xml',
        'views/account_view.xml',
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/product_category_view.xml',
        'views/product_pricelist_item.xml',
        'views/product_supplierinfo.xml',
        'views/hide_vendor_view.xml',
        'views/hr_expense_view.xml',
        'views/hr_view.xml',
        'views/hr_payroll_view.xml',
        'views/crm_view.xml',
        'views/sale_adv_payment_view.xml',
        'views/company_view.xml',
        'views/hr_job_view.xml',
        'reports/master_template.xml',
        'reports/saleorder_document.xml', 
        'reports/invoice_proforma_document.xml',
        'reports/delivery_document.xml',
        'reports/delivery_document_copy.xml',
        'reports/picking_document.xml',
        #'reports/picking_document_incl_supplier.xml',
        'reports/pick_delivery_set_document.xml',
        'reports/inventory_document.xml',
        'reports/invoice_document.xml',
        'reports/invoice_summary.xml',
        'reports/invoice_partner_summary.xml',
        'reports/product_catalog_document.xml',
        'reports/product_label_document.xml',
        'reports/partner_summary.xml',
        'reports/payslip_document.xml',
        'reports/mass_picking_document.xml',
        'reports/mass_delivery_document.xml',
        'reports/mass_pick_delivery_set_document.xml',
        'reports/mass_payslip_document.xml',
        'reports/expense_sheet_document.xml',
        'reports/rma_label_document.xml',
        'reports/email_template.xml',
        'reports/sms_wa_template.xml',
        'reports/payment_document.xml',
        'reports/attendance_document.xml',
        'wizard/product_label_print_wizard.xml',
        'wizard/int_transfer_wizard.xml',
        'wizard/product_image_upload_wizard.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
}
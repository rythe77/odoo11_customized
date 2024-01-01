# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    #Additional data to input to customer data
    id_number = fields.Char(string="Nomor Identitas (KTP)")
    is_pkp = fields.Boolean('Pengusaha Kena Pajak', default=False,
        help='Centang jika perusahaan terdaftar sebagai pengusaha kena pajak')
    name_npwp = fields.Char(string="Nama NPWP")
    address_npwp = fields.Char(string="Alamat NPWP")
    company_register = fields.Selection([
        ('individual', 'Perseorangan/UD'),
        ('firm', 'Firma'),
        ('cv', 'CV'),
        ('pt', 'Perseroan Terbatas'),
        ('ptn', 'Persero/Perusahaan Daerah/Perum'),
        ('coop', 'Koperasi'),
        ('npo', 'Yayasan')],
        string='Bentuk Badan Usaha',
        help="Bentuk badan usaha yang terdaftar di administrasi pemerintahan")
    register_date = fields.Date(string="Tanggal Pengukuhan")
    preferred_transporter = fields.Many2one('res.partner', string='Ekspedisi Pilihan', domain=[('transporter', '=', True)])
    interested_product = fields.Text(string='Jenis Barang yang Diambil')
    sign_speciment = fields.Binary("Spesimen Tanda Tangan", attachment=True)

    #Create new fields
    x_call_freq = fields.Selection([
        ('priority', 'A - Priority'),
        ('urgent', 'B - Urgent'),
        ('less_urgent', 'C - Less Urgent'),
        ('common', 'D - common'),
        ('not_urgent', 'E - Not Urgent')],
        string='Grade', default='common',
        help="Show how urgent it is to call the customer")

    x_notification_method = fields.Selection([
        ('none', 'Tidak Dinotifikasi'),
        ('email', 'Email'),
        ('wa', 'WA'),
        ('sms', 'SMS')],
        string='Metode Notifikasi', default='none',
        help="Pilih salah satu metode notifikasi yang diinginkan pelanggan.")
    x_is_notify_so = fields.Boolean('Konfirmasi Order', default=True,
        help='Otomatis kirimkan notifikasi ke pelanggan ketika order dikonfirmasi')
    x_is_notify_do = fields.Boolean('Validasi Surat Jalan', default=True,
        help='Otomatis kirimkan notifikasi ke pelanggan ketika surat jalan divalidasi')
    x_is_notify_inv = fields.Boolean('Validasi Faktur', default=True,
        help='Otomatis kirimkan notifikasi ke pelanggan ketika faktur divalidasi')
    x_is_notify_pay = fields.Boolean('Konfirmasi Pembayaran', default=True,
        help='Otomatis kirimkan notifikasi ke pelanggan ketika penerimaan pembayaran dikonfirmasi')


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_name = fields.Char(string="Nama Rekening")

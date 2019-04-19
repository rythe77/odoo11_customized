# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    #Create new fields
    x_call_freq = fields.Selection([
        ('urgent', 'Urgent'),
        ('less_urgent', 'Less Urgent'),
        ('common', 'common'),
        ('not_urgent', 'Not Urgent')],
        string='To Call', default='not_urgent',
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

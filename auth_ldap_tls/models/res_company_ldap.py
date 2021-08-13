# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ldap

from odoo import api, fields, models


class CompanyLDAP(models.Model):
    _inherit = "res.company.ldap"

    cacert_path = fields.Char(string='Path to CACERT file')

    @api.multi
    def get_ldap_dicts(self):
        """
        Add cacert_path to ldap_dicts
        """
        results = super(CompanyLDAP, self).get_ldap_dicts()
        ldaps = self.sudo().search([('ldap_server', '!=', False)], order='sequence')
        cacert_paths = ldaps.read(['cacert_path'])
        for i in range(len(results)):
            results[i].update(cacert_paths[i])
        return results

    def connect(self, conf):
        """
        Override odoo connect function to fix StartTLS
        Connect to an LDAP server specified by an ldap
        configuration dictionary.

        :param dict conf: LDAP configuration
        :return: an LDAP object
        """

        uri = 'ldap://%s:%d' % (conf['ldap_server'], conf['ldap_server_port'])

        connection = ldap.initialize(uri)
        if conf['ldap_tls']:
            connection.set_option(ldap.OPT_X_TLS_CACERTFILE, conf['cacert_path'])
            connection.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
            connection.start_tls_s()
        return connection

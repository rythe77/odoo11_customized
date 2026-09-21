# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os

import ldap

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# When this environment variable is truthy, get_ldap_dicts() returns nothing and
# every LDAP code path goes inert: res.users._login() and check_credentials()
# both take their server list from it. The development stack sets this so that a
# production dump restored into a dev database -- which carries the
# res.company.ldap rows along with it -- cannot make every login attempt a bind
# against the production LDAP server.
DISABLE_ENV_VAR = 'ODOO_DISABLE_LDAP'


def _ldap_disabled():
    """True when ODOO_DISABLE_LDAP holds 1/true/yes (case-insensitive)."""
    return os.environ.get(DISABLE_ENV_VAR, '').strip().lower() in ('1', 'true', 'yes')


class CompanyLDAP(models.Model):
    _inherit = "res.company.ldap"

    cacert_path = fields.Char(string='Path to CACERT file')

    @api.multi
    def get_ldap_dicts(self):
        """
        Add cacert_path to ldap_dicts
        """
        if _ldap_disabled():
            _logger.info(
                "LDAP disabled by %s: ignoring all res.company.ldap entries",
                DISABLE_ENV_VAR,
            )
            return []
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

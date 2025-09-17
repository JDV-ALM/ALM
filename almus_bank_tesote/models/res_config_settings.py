# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # API Configuration
    tesote_api_token = fields.Char(
        string='Tesote API Token',
        config_parameter='tesote.api_token'
    )
    tesote_api_url = fields.Char(
        string='Tesote API URL',
        config_parameter='tesote.api_url',
        default='https://equipo.tesote.com/api/v2'
    )
    
    # Sync Configuration  
    tesote_auto_sync = fields.Boolean(
        string='Automatic Daily Sync',
        config_parameter='tesote.auto_sync'
    )
    tesote_sync_days = fields.Integer(
        string='Days to Sync',
        config_parameter='tesote.sync_days',
        default=7,
        help="Number of days to look back when syncing transactions"
    )
    
    # Webhook Configuration
    tesote_webhook_enabled = fields.Boolean(
        string='Enable Webhooks',
        config_parameter='tesote.webhook_enabled'
    )
    
    # Status fields
    tesote_connection_status = fields.Char(
        string='Connection Status',
        compute='_compute_tesote_status'
    )
    tesote_accounts_count = fields.Integer(
        string='Configured Accounts',
        compute='_compute_tesote_status'
    )
    tesote_last_sync = fields.Datetime(
        string='Last Sync',
        compute='_compute_tesote_status'
    )
    
    @api.depends('tesote_api_token')
    def _compute_tesote_status(self):
        for record in self:
            # Count configured accounts
            accounts = self.env['tesote.account'].search([])
            record.tesote_accounts_count = len(accounts)
            
            # Get last sync
            last_account = accounts.filtered('last_sync').sorted('last_sync', reverse=True)[:1]
            record.tesote_last_sync = last_account.last_sync if last_account else False
            
            # Connection status
            if not record.tesote_api_token:
                record.tesote_connection_status = 'Not configured'
            else:
                record.tesote_connection_status = 'Token configured'
    
    def action_test_tesote_connection(self):
        """Test connection to Tesote API"""
        self.ensure_one()
        
        if not self.tesote_api_token:
            raise UserError(_("Please enter an API token first"))
        
        # Import correctly from the addon path
        from odoo.addons.almus_bank_tesote.models import tesote_connector
        
        connector = tesote_connector.TesoteConnector(
            self.tesote_api_token,
            self.tesote_api_url,
            self.env
        )
        
        success, message = connector.test_connection()
        
        if success:
            # Try to fetch accounts
            try:
                accounts = connector.get_accounts()
                message = _("Connection successful! Found %d accounts") % len(accounts)
                notification_type = 'success'
            except Exception as e:
                message = _("Connection works but failed to fetch accounts: %s") % str(e)
                notification_type = 'warning'
        else:
            notification_type = 'danger'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection Test'),
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }
    
    def action_refresh_tesote_accounts(self):
        """Refresh accounts from Tesote API"""
        self.ensure_one()
        
        if not self.tesote_api_token:
            raise UserError(_("Please configure the API token first"))
        
        self.env['tesote.account'].action_refresh_accounts()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Accounts Refreshed'),
                'message': _('Tesote accounts have been refreshed successfully'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_open_tesote_accounts(self):
        """Open Tesote accounts configuration"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tesote Bank Accounts'),
            'res_model': 'tesote.account',
            'view_mode': 'tree,form',
            'view_id': self.env.ref('almus_bank_tesote.view_tesote_account_tree').id,
            'context': {'create': False}
        }
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import hashlib
import hmac
import json
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class TesoteWebhook(models.Model):
    _name = 'tesote.webhook'
    _description = 'Tesote Webhook Configuration'
    _rec_name = 'webhook_url'
    
    active = fields.Boolean('Active', default=True)
    webhook_url = fields.Char('Webhook URL', compute='_compute_webhook_url', store=False)
    webhook_secret = fields.Char('Webhook Secret', required=True, 
                                 default=lambda self: self._generate_secret())
    
    # Event subscriptions
    subscribe_account_update = fields.Boolean('Account Updates', default=True)
    subscribe_transaction_new = fields.Boolean('New Transactions', default=True)
    subscribe_balance_update = fields.Boolean('Balance Updates', default=True)
    
    # Statistics
    last_received = fields.Datetime('Last Event Received', readonly=True)
    events_received = fields.Integer('Events Received', readonly=True, default=0)
    
    @api.depends('webhook_secret')
    def _compute_webhook_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.id:
                record.webhook_url = f"{base_url}/tesote/webhook/{record.id}"
            else:
                record.webhook_url = f"{base_url}/tesote/webhook/[ID]"
    
    @api.model
    def _generate_secret(self):
        """Generate a secure random secret for webhook validation"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def verify_signature(self, payload, signature):
        """Verify webhook signature from Tesote"""
        self.ensure_one()
        expected_sig = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature)
    
    def process_webhook_event(self, event_type, payload):
        """Process incoming webhook event"""
        self.ensure_one()
        
        # Update statistics
        self.write({
            'last_received': fields.Datetime.now(),
            'events_received': self.events_received + 1
        })
        
        _logger.info(f"Processing Tesote webhook event: {event_type}")
        
        if event_type == 'transaction.created' and self.subscribe_transaction_new:
            self._process_new_transaction(payload)
        elif event_type == 'account.updated' and self.subscribe_account_update:
            self._process_account_update(payload)
        elif event_type == 'balance.updated' and self.subscribe_balance_update:
            self._process_balance_update(payload)
    
    def _process_new_transaction(self, payload):
        """Process new transaction webhook"""
        account_id = payload.get('account_id')
        if not account_id:
            return
        
        account = self.env['tesote.account'].search([
            ('tesote_id', '=', account_id),
            ('active', '=', True)
        ], limit=1)
        
        if account and account.journal_id:
            # Trigger sync for this specific account
            account.with_context(from_webhook=True)._sync_transactions(days_back=1)
    
    def _process_account_update(self, payload):
        """Process account update webhook"""
        # Refresh account data from Tesote
        self.env['tesote.account'].action_refresh_accounts()
    
    def _process_balance_update(self, payload):
        """Process balance update webhook"""
        account_id = payload.get('account_id')
        balance_cents = payload.get('balance_cents')
        
        if account_id and balance_cents is not None:
            account = self.env['tesote.account'].search([
                ('tesote_id', '=', account_id)
            ], limit=1)
            
            if account:
                account.write({'balance_cents': balance_cents})
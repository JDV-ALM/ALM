# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging
import json

_logger = logging.getLogger(__name__)

class TesoteAccount(models.Model):
    _name = 'tesote.account'
    _description = 'Tesote Bank Account'
    _rec_name = 'display_name'
    _order = 'bank_name, masked_account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Tesote Fields (readonly)
    tesote_id = fields.Char('Tesote ID', required=True, readonly=True, index=True)
    name = fields.Char('Account Name', readonly=True, tracking=True)
    masked_account = fields.Char('Account Number', readonly=True)
    currency = fields.Selection([
        ('VES', 'VES - Bolívar'),
        ('USD', 'USD - Dollar')
    ], readonly=True, required=True)
    bank_name = fields.Char('Bank', readonly=True)
    legal_entity_id = fields.Char('Legal Entity ID', readonly=True)
    legal_entity_name = fields.Char('Legal Entity', readonly=True)
    
    # Balance
    balance_cents = fields.Integer('Balance (cents)', readonly=True)
    balance = fields.Monetary('Balance', compute='_compute_balance', 
                             currency_field='currency_id', store=True)
    
    # Manual Mapping (editable)
    company_id = fields.Many2one('res.company', string='Company', 
                                 required=True, default=lambda self: self.env.company,
                                 tracking=True)
    journal_id = fields.Many2one('account.journal', string='Bank Journal',
                                 domain="[('type','=','bank'), ('company_id','=',company_id)]",
                                 tracking=True)
    statement_prefix = fields.Char('Statement Prefix', default='TESOTE/',
                                  help="Prefix for generated bank statements")
    active = fields.Boolean('Active', default=True, tracking=True)
    
    # Synchronization Control
    last_sync = fields.Datetime('Last Sync', readonly=True)
    last_transaction_id = fields.Char('Last Transaction ID', readonly=True)
    last_transaction_date = fields.Date('Last Transaction Date', readonly=True)
    sync_status = fields.Selection([
        ('never', 'Never Synchronized'),
        ('syncing', 'Synchronizing'),
        ('success', 'Success'),
        ('error', 'Error')
    ], default='never', readonly=True, tracking=True)
    sync_error_message = fields.Text('Last Error', readonly=True)
    
    # Computed fields
    display_name = fields.Char(compute='_compute_display_name', store=True)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency_id', store=True)
    statement_ids = fields.One2many('account.bank.statement', 'tesote_account_id', 
                                    string='Bank Statements', readonly=True)
    statement_count = fields.Integer('Statements', compute='_compute_statement_count')
    
    @api.depends('bank_name', 'masked_account', 'legal_entity_name')
    def _compute_display_name(self):
        for record in self:
            parts = []
            if record.bank_name:
                parts.append(record.bank_name)
            if record.masked_account:
                parts.append(f"***{record.masked_account[-4:]}")
            if record.legal_entity_name:
                parts.append(f"({record.legal_entity_name})")
            record.display_name = " ".join(parts) or "Tesote Account"
    
    @api.depends('currency')
    def _compute_currency_id(self):
        for record in self:
            if record.currency:
                currency = self.env['res.currency'].search([('name', '=', record.currency)], limit=1)
                if not currency and record.currency == 'VES':
                    # Create VES currency if it doesn't exist
                    currency = self.env['res.currency'].sudo().create({
                        'name': 'VES',
                        'symbol': 'Bs.',
                        'position': 'before',
                        'rounding': 0.01,
                    })
                record.currency_id = currency.id if currency else False
            else:
                record.currency_id = False
    
    @api.depends('balance_cents', 'currency_id')
    def _compute_balance(self):
        for record in self:
            record.balance = record.balance_cents / 100.0 if record.balance_cents else 0.0
    
    @api.depends('statement_ids')
    def _compute_statement_count(self):
        for record in self:
            record.statement_count = len(record.statement_ids)
    
    @api.constrains('journal_id')
    def _check_journal_currency(self):
        for record in self:
            if record.journal_id and record.currency_id:
                journal_currency = record.journal_id.currency_id or record.journal_id.company_id.currency_id
                if journal_currency != record.currency_id:
                    raise ValidationError(
                        _("The journal currency (%s) must match the Tesote account currency (%s)") % 
                        (journal_currency.name, record.currency_id.name)
                    )
    
    def action_sync_transactions(self):
        """Manual sync button action"""
        self.ensure_one()
        if not self.journal_id:
            raise UserError(_("Please configure a bank journal for this account before syncing."))
        
        self.with_context(manual_sync=True)._sync_transactions()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Synchronization Started'),
                'message': _('Transaction synchronization has been initiated for %s') % self.display_name,
                'type': 'info',
                'sticky': False,
            }
        }
    
    def _sync_transactions(self, days_back=None):
        """
        Sync transactions from Tesote API
        Creates bank statements with transactions
        """
        self.ensure_one()
        
        if not self.journal_id:
            _logger.warning(f"No journal configured for Tesote account {self.display_name}")
            return False
        
        try:
            # Update status
            self.write({
                'sync_status': 'syncing',
                'sync_error_message': False
            })
            
            # Get API connector
            IrConfigParam = self.env['ir.config_parameter'].sudo()
            token = IrConfigParam.get_param('tesote.api_token')
            api_url = IrConfigParam.get_param('tesote.api_url', 'https://equipo.tesote.com/api/v2')
            
            if not token:
                raise UserError(_("Tesote API token not configured"))
            
            # Import connector correctly
            from odoo.addons.almus_bank_tesote.models import tesote_connector
            connector = tesote_connector.TesoteConnector(token, api_url, self.env)
            
            # Determine date range
            if days_back is None:
                days_back = int(IrConfigParam.get_param('tesote.sync_days', 7))
            
            end_date = fields.Date.context_today(self)
            start_date = end_date - timedelta(days=days_back)
            
            # Use incremental sync if we have a last transaction ID
            after_id = self.last_transaction_id if not self.env.context.get('force_full_sync') else None
            
            # Fetch transactions
            result = connector.get_transactions(
                self.tesote_id,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                after_id=after_id
            )
            
            transactions = result.get('transactions', [])
            
            if transactions:
                self._process_transactions(transactions)
                
                # Update last transaction ID (use the newest transaction)
                last_transaction = max(transactions, key=lambda x: x.get('id', ''))
                self.write({
                    'last_transaction_id': last_transaction.get('id'),
                    'last_transaction_date': last_transaction.get('date'),
                })
            
            # Update sync status
            self.write({
                'last_sync': fields.Datetime.now(),
                'sync_status': 'success',
            })
            
            _logger.info(f"Successfully synced {len(transactions)} transactions for {self.display_name}")
            return True
            
        except Exception as e:
            _logger.error(f"Error syncing transactions for {self.display_name}: {str(e)}")
            self.write({
                'sync_status': 'error',
                'sync_error_message': str(e),
            })
            if self.env.context.get('manual_sync'):
                raise UserError(_("Synchronization failed: %s") % str(e))
            return False
    
    def _process_transactions(self, transactions):
        """
        Process transactions and create/update bank statements
        Groups transactions by date and creates one statement per day
        """
        self.ensure_one()
        
        if not transactions:
            return
        
        # Group transactions by date
        transactions_by_date = {}
        for trans in transactions:
            date = fields.Date.from_string(trans.get('date'))
            if date not in transactions_by_date:
                transactions_by_date[date] = []
            transactions_by_date[date].append(trans)
        
        BankStatement = self.env['account.bank.statement']
        
        for date, day_transactions in transactions_by_date.items():
            # Find or create statement for this date
            statement_name = f"{self.statement_prefix}{date.strftime('%Y%m%d')}"
            statement = BankStatement.search([
                ('name', '=', statement_name),
                ('journal_id', '=', self.journal_id.id),
                ('date', '=', date)
            ], limit=1)
            
            if not statement:
                # Create new statement
                statement = BankStatement.create({
                    'name': statement_name,
                    'date': date,
                    'journal_id': self.journal_id.id,
                    'tesote_account_id': self.id,
                })
            
            # Process each transaction
            for trans in day_transactions:
                self._create_statement_line(statement, trans)
    
    def _create_statement_line(self, statement, transaction):
        """Create or update a bank statement line from a Tesote transaction"""
        BankStatementLine = self.env['account.bank.statement.line']
        
        # Check if line already exists (avoid duplicates)
        existing_line = BankStatementLine.search([
            ('statement_id', '=', statement.id),
            ('ref', '=', transaction.get('id'))
        ], limit=1)
        
        if existing_line:
            return existing_line
        
        # Determine amount (convert from cents)
        amount_cents = transaction.get('amount_cents', 0)
        amount = amount_cents / 100.0
        
        # Create statement line
        line_vals = {
            'statement_id': statement.id,
            'date': transaction.get('date'),
            'payment_ref': transaction.get('description', ''),
            'ref': transaction.get('id'),
            'amount': amount,
            'partner_name': transaction.get('counterpart_name', ''),
        }
        
        # Try to find partner
        if transaction.get('counterpart_document'):
            partner = self.env['res.partner'].search([
                '|',
                ('vat', '=', transaction.get('counterpart_document')),
                ('ref', '=', transaction.get('counterpart_document'))
            ], limit=1)
            if partner:
                line_vals['partner_id'] = partner.id
        
        return BankStatementLine.create(line_vals)
    
    @api.model
    def cron_sync_all_accounts(self):
        """Cron job to sync all active accounts"""
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        
        if not IrConfigParam.get_param('tesote.auto_sync'):
            _logger.info("Tesote auto-sync is disabled")
            return
        
        accounts = self.search([
            ('active', '=', True),
            ('journal_id', '!=', False)
        ])
        
        _logger.info(f"Starting Tesote sync for {len(accounts)} accounts")
        
        for account in accounts:
            try:
                account._sync_transactions()
            except Exception as e:
                _logger.error(f"Failed to sync account {account.display_name}: {str(e)}")
                continue
    
    def action_view_statements(self):
        """Action to view related bank statements"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bank Statements'),
            'res_model': 'account.bank.statement',
            'view_mode': 'tree,form',
            'domain': [('tesote_account_id', '=', self.id)],
            'context': {'default_journal_id': self.journal_id.id},
        }
    
    @api.model
    def action_refresh_accounts(self):
        """Refresh accounts from Tesote API - Class method"""
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        token = IrConfigParam.get_param('tesote.api_token')
        api_url = IrConfigParam.get_param('tesote.api_url')
        
        if not token:
            raise UserError(_("Please configure the Tesote API token first"))
        
        # Import connector correctly
        from odoo.addons.almus_bank_tesote.models import tesote_connector
        connector = tesote_connector.TesoteConnector(token, api_url, self.env)
        
        try:
            accounts_data = connector.get_accounts()
            
            for account_data in accounts_data:
                # Check if account exists
                existing = self.search([('tesote_id', '=', account_data.get('id'))], limit=1)
                
                vals = {
                    'tesote_id': account_data.get('id'),
                    'name': account_data.get('name'),
                    'masked_account': account_data.get('masked_account'),
                    'currency': account_data.get('currency'),
                    'bank_name': account_data.get('bank_name'),
                    'legal_entity_id': account_data.get('legal_entity_id'),
                    'legal_entity_name': account_data.get('legal_entity_name'),
                    'balance_cents': account_data.get('balance_cents', 0),
                }
                
                if existing:
                    # Update existing account (don't overwrite mapping)
                    existing.write(vals)
                else:
                    # Create new account
                    vals['company_id'] = self.env.company.id
                    self.create(vals)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Accounts refreshed successfully. Found %d accounts.') % len(accounts_data),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_("Failed to refresh accounts: %s") % str(e))
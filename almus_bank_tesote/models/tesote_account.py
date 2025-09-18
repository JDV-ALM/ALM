class TesoteAccount(models.Model):
    """Cuenta bancaria de Tesote mapeada a diario Odoo"""
    _name = 'tesote.account'
    _description = 'Cuenta Bancaria Tesote'
    _rec_name = 'display_name'
    _order = 'bank_name, masked_account'
    
    # Identificación Tesote
    tesote_id = fields.Char('ID Tesote', required=True, readonly=True)
    bank_name = fields.Char('Banco', readonly=True)
    masked_account = fields.Char('Cuenta', readonly=True)
    currency = fields.Char('Moneda', readonly=True)
    legal_entity_name = fields.Char('Titular', readonly=True)
    balance = fields.Float('Balance', readonly=True)
    
    # Mapeo Odoo
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Diario Contable',
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
        help="Seleccione el diario donde se importarán las transacciones"
    )
    active = fields.Boolean('Activo', default=True)
    
    # Sincronización
    last_sync = fields.Datetime('Última Sincronización')
    sync_status = fields.Selection([
        ('never', 'Nunca'),
        ('success', 'Exitoso'),
        ('error', 'Error'),
    ], string='Estado', default='never', readonly=True)
    sync_error = fields.Text('Mensaje de Error', readonly=True)
    transaction_count = fields.Integer('Transacciones Importadas', readonly=True)
    
    # Display name computado
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('bank_name', 'masked_account', 'currency')
    def _compute_display_name(self):
        for record in self:
            parts = []
            if record.bank_name:
                parts.append(record.bank_name)
            if record.masked_account:
                parts.append(f"***{record.masked_account[-4:]}")
            if record.currency:
                parts.append(f"[{record.currency}]")
            record.display_name = ' '.join(parts) or 'Cuenta Tesote'
    
    @api.model
    def refresh_accounts_from_api(self):
        """Actualizar cuentas desde API"""
        # Obtener configuración
        config = self.env['tesote.config'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not config:
            raise UserError(_("Configure Tesote primero en el menú de configuración"))
        
        if not config.api_token:
            raise UserError(_("Token de API no configurado"))
        
        # Conectar con API
        from . import tesote_connector
        connector = tesote_connector.TesoteConnector(config.api_token, config.api_url)
        
        # Obtener cuentas con límite
        accounts = connector.get_accounts(limit=50)
        if not accounts:
            raise UserError(_("No se encontraron cuentas o error de conexión"))
        
        created = 0
        updated = 0
        
        for acc_data in accounts:
            tesote_id = acc_data.get('id')
            if not tesote_id:
                continue
            
            existing = self.search([
                ('tesote_id', '=', tesote_id),
                ('company_id', '=', config.company_id.id)
            ], limit=1)
            
            vals = {
                'tesote_id': tesote_id,
                'bank_name': acc_data.get('bank_name', ''),
                'masked_account': acc_data.get('masked_account', ''),
                'currency': acc_data.get('currency', 'VES'),
                'legal_entity_name': acc_data.get('legal_entity_name', ''),
                'balance': acc_data.get('balance', 0.0),
                'company_id': config.company_id.id,
            }
            
            if existing:
                existing.write(vals)
                updated += 1
            else:
                self.create(vals)
                created += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("✓ %d cuentas creadas, %d actualizadas") % (created, updated),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_sync_transactions(self):
        """Sincronizar transacciones de cuentas seleccionadas"""
        # Obtener configuración
        config = self.env['tesote.config'].search([
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        if not config:
            raise UserError(_("Configure Tesote primero"))
        
        # Procesar cada cuenta
        for account in self:
            if not account.journal_id:
                _logger.warning(f"Cuenta {account.display_name} sin diario configurado")
                continue
            
            try:
                account._sync_transactions(config)
                account.write({
                    'sync_status': 'success',
                    'sync_error': False,
                    'last_sync': fields.Datetime.now()
                })
            except Exception as e:
                error_msg = str(e)[:500]
                _logger.error(f"Error sincronizando {account.display_name}: {error_msg}")
                account.write({
                    'sync_status': 'error',
                    'sync_error': error_msg
                })
    
    def _sync_transactions(self, config):
        """Sincronizar transacciones usando configuración"""
        self.ensure_one()
        
        from . import tesote_connector
        connector = tesote_connector.TesoteConnector(config.api_token, config.api_url)
        
        # Calcular rango de fechas
        from datetime import datetime, timedelta
        date_to = datetime.now()
        
        if self.last_sync:
            date_from = fields.Datetime.from_string(self.last_sync)
        else:
            days_back = min(config.sync_days, 30)  # Máximo 30 días
            date_from = date_to - timedelta(days=days_back)
        
        # Obtener transacciones con límites seguros
        transactions = connector.get_transactions(
            account_id=self.tesote_id,
            date_from=date_from,
            date_to=date_to
        )
        
        if not transactions:
            _logger.info(f"Sin transacciones nuevas para {self.display_name}")
            return
        
        # Crear o actualizar extracto bancario
        self._create_bank_statement(transactions)
        
        # Actualizar contador
        self.transaction_count = len(transactions)
        
        # Actualizar balance si es posible
        new_balance = connector.get_account_balance(self.tesote_id)
        if new_balance is not None:
            self.balance = new_balance
    
    def _create_bank_statement(self, transactions):
        """Crear extracto bancario con transacciones"""
        self.ensure_one()
        
        if not transactions:
            return
        
        # Agrupar por fecha
        from collections import defaultdict
        by_date = defaultdict(list)
        
        for txn in transactions:
            date = txn.get('date', '')[:10]
            if date:
                by_date[date].append(txn)
        
        # Crear extracto
        dates = sorted(by_date.keys())
        statement_name = f"TESOTE/{dates[0]}/{dates[-1]}"
        
        # Buscar o crear extracto
        Statement = self.env['account.bank.statement']
        statement = Statement.search([
            ('name', '=', statement_name),
            ('journal_id', '=', self.journal_id.id)
        ], limit=1)
        
        if not statement:
            statement = Statement.create({
                'name': statement_name,
                'journal_id': self.journal_id.id,
                'date': dates[-1],
            })
        
        # Agregar líneas
        StatementLine = self.env['account.bank.statement.line']
        
        for date_str in dates:
            for txn in by_date[date_str]:
                # Verificar si ya existe
                ref = txn.get('reference', txn.get('id'))
                existing = StatementLine.search([
                    ('statement_id', '=', statement.id),
                    ('ref', '=', ref)
                ], limit=1)
                
                if existing:
                    continue
                
                # Determinar monto (positivo = ingreso, negativo = egreso)
                amount = float(txn.get('amount', 0))
                if txn.get('type') == 'debit':
                    amount = -abs(amount)
                elif txn.get('type') == 'credit':
                    amount = abs(amount)
                
                # Crear línea
                StatementLine.create({
                    'statement_id': statement.id,
                    'date': date_str,
                    'name': txn.get('description', 'Transacción')[:200],
                    'ref': ref,
                    'amount': amount,
                })
        
        return statement
    
    @api.model
    def cron_sync_all_accounts(self):
        """Cron para sincronización automática diaria"""
        # Buscar configuraciones con auto_sync activo
        configs = self.env['tesote.config'].search([('auto_sync', '=', True)])
        
        for config in configs:
            accounts = self.search([
                ('company_id', '=', config.company_id.id),
                ('journal_id', '!=', False),
                ('active', '=', True)
            ])
            
            if accounts:
                _logger.info(f"Sincronización automática: {len(accounts)} cuentas de {config.company_id.name}")
                accounts.with_context(tesote_config_id=config.id).action_sync_transactions()
    
    @api.model
    def process_webhook_transaction(self, account_id, transaction_data):
        """
        Procesar transacción desde webhook
        Llamado desde automatización de Odoo
        """
        account = self.search([('tesote_id', '=', account_id)], limit=1)
        if not account:
            _logger.warning(f"Cuenta {account_id} no encontrada para webhook")
            return False
        
        if not account.journal_id:
            _logger.warning(f"Cuenta {account.display_name} sin diario configurado")
            return False
        
        # Sincronizar solo esta cuenta
        config = self.env['tesote.config'].search([
            ('company_id', '=', account.company_id.id)
        ], limit=1)
        
        if config:
            account.with_context(tesote_config_id=config.id).action_sync_transactions()
            return True
        
        return False
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class TesoteConfig(models.Model):
    """
    Configuración de Tesote - Modelo independiente
    Un solo registro de configuración por compañía
    """
    _name = 'tesote.config'
    _description = 'Configuración Tesote'
    _rec_name = 'company_id'
    
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade'
    )
    
    # Configuración API
    api_token = fields.Char(
        string='Token API',
        required=True,
        help="Bearer token proporcionado por Tesote"
    )
    api_url = fields.Char(
        string='URL API',
        default='https://equipo.tesote.com/api/v2',
        required=True,
        help="URL base de la API de Tesote"
    )
    
    # Configuración de sincronización
    auto_sync = fields.Boolean(
        string='Sincronización Automática',
        default=True,
        help="Activar sincronización diaria automática"
    )
    sync_days = fields.Integer(
        string='Días a Sincronizar',
        default=7,
        help="Número de días hacia atrás para sincronizar transacciones"
    )
    max_transactions = fields.Integer(
        string='Límite de Transacciones',
        default=100,
        help="Número máximo de transacciones por sincronización"
    )
    
    # Estado
    last_connection_test = fields.Datetime('Última Prueba de Conexión')
    connection_status = fields.Selection([
        ('not_tested', 'No Probado'),
        ('success', 'Conectado'),
        ('error', 'Error de Conexión'),
    ], string='Estado de Conexión', default='not_tested')
    
    # Información de webhook para mostrar
    webhook_url = fields.Char(
        string='URL Webhook',
        compute='_compute_webhook_url',
        help="Configure esta URL en Tezzote para recibir notificaciones"
    )
    
    _sql_constraints = [
        ('company_uniq', 'unique (company_id)', 'Solo puede existir una configuración por compañía'),
    ]
    
    @api.depends('company_id')
    def _compute_webhook_url(self):
        """Generar URL del webhook para configurar en Tesote"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            # URL del webhook usando automatizaciones de Odoo
            record.webhook_url = f"{base_url}/mail/webhook/tesote"
    
    def action_test_connection(self):
        """Probar conexión con Tesote API"""
        self.ensure_one()
        
        if not self.api_token:
            raise UserError(_("Por favor configure el token de API"))
        
        try:
            from ..models import tesote_connector
            connector = tesote_connector.TesoteConnector(self.api_token, self.api_url)
            
            if connector.test_connection():
                self.write({
                    'connection_status': 'success',
                    'last_connection_test': fields.Datetime.now()
                })
                message = _("✓ Conexión exitosa con Tesote")
                msg_type = 'success'
            else:
                self.write({'connection_status': 'error'})
                message = _("✗ No se pudo conectar con Tesote")
                msg_type = 'danger'
                
        except Exception as e:
            self.write({'connection_status': 'error'})
            message = _("✗ Error: %s") % str(e)[:100]
            msg_type = 'danger'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': msg_type,
                'sticky': False,
            }
        }
    
    def action_refresh_accounts(self):
        """Actualizar lista de cuentas desde Tesote"""
        self.ensure_one()
        
        if self.connection_status != 'success':
            self.action_test_connection()
        
        if self.connection_status != 'success':
            raise UserError(_("Primero debe establecer conexión con Tesote"))
        
        return self.env['tesote.account'].with_context(
            tesote_config_id=self.id
        ).refresh_accounts_from_api()
    
    def action_open_accounts(self):
        """Abrir vista de cuentas"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mapeo de Cuentas'),
            'res_model': 'tesote.account',
            'view_mode': 'tree',
            'domain': [('company_id', '=', self.company_id.id)],
            'context': {'default_company_id': self.company_id.id}
        }
    
    def action_sync_all(self):
        """Sincronizar todas las cuentas manualmente"""
        self.ensure_one()
        accounts = self.env['tesote.account'].search([
            ('company_id', '=', self.company_id.id),
            ('journal_id', '!=', False),
            ('active', '=', True)
        ])
        
        if not accounts:
            raise UserError(_("No hay cuentas configuradas para sincronizar"))
        
        accounts.with_context(
            tesote_config_id=self.id
        ).action_sync_transactions()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("Sincronización iniciada para %d cuentas") % len(accounts),
                'type': 'info',
            }
        }
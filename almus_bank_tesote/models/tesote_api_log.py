# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta

class TesoteApiLog(models.Model):
    _name = 'tesote.api.log'
    _description = 'Tesote API Request Log'
    _order = 'create_date desc'
    _rec_name = 'endpoint'
    
    endpoint = fields.Char('Endpoint', required=True)
    method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE')
    ], required=True)
    request_time = fields.Datetime('Request Time', default=fields.Datetime.now)
    response_time = fields.Integer('Response Time (ms)')
    status_code = fields.Integer('Status Code')
    error_message = fields.Text('Error Message')
    account_id = fields.Many2one('tesote.account', 'Account', ondelete='cascade')
    
    def name_get(self):
        """Custom name display for logs"""
        result = []
        for record in self:
            name = f"{record.method} {record.endpoint}"
            if record.status_code:
                name += f" ({record.status_code})"
            result.append((record.id, name))
        return result
    
    @api.autovacuum
    def _gc_tesote_logs(self):
        """Garbage collect old logs (keep only last 30 days)"""
        limit_date = fields.Datetime.now() - timedelta(days=30)
        return self.search([('create_date', '<', limit_date)]).unlink()
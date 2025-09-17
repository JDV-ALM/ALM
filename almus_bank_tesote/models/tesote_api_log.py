# -*- coding: utf-8 -*-
from odoo import models, fields

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
    account_id = fields.Many2one('tesote.account', 'Account')

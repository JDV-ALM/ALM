# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    
    tesote_account_id = fields.Many2one('tesote.account', string='Tesote Account',
                                        readonly=True, ondelete='set null')

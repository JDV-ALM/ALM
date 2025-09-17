# -*- coding: utf-8 -*-
from . import controllers
from . import models

def pre_init_hook(cr):
    """Pre-initialization hook"""
    # Create VES currency if it doesn't exist
    cr.execute("""
        INSERT INTO res_currency (name, symbol, position, rounding, active, create_uid, write_uid, create_date, write_date)
        SELECT 'VES', 'Bs.', 'before', 0.01, true, 1, 1, NOW(), NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM res_currency WHERE name = 'VES'
        )
    """)

def post_init_hook(cr, registry):
    """Post-initialization hook"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create default webhook configuration
    Webhook = env['tesote.webhook']
    if not Webhook.search([]):
        Webhook.create({
            'active': False,  # Disabled by default
            'subscribe_account_update': True,
            'subscribe_transaction_new': True,
            'subscribe_balance_update': True,
        })
    
    # Enable cron if auto_sync is enabled
    IrConfigParam = env['ir.config_parameter'].sudo()
    if IrConfigParam.get_param('tesote.auto_sync'):
        cron = env.ref('almus_bank_tesote.ir_cron_tesote_sync', raise_if_not_found=False)
        if cron:
            cron.active = True

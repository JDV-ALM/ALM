# -*- coding: utf-8 -*-
from . import controllers
from . import models

def pre_init_hook(env):
    """Pre-initialization hook - Odoo 17 compatible"""
    # En Odoo 17, el hook recibe env, no cr
    cr = env.cr
    # Create VES currency if it doesn't exist
    cr.execute("""
        INSERT INTO res_currency (name, symbol, position, rounding, active, create_uid, write_uid, create_date, write_date)
        SELECT 'VES', 'Bs.', 'before', 0.01, true, 1, 1, NOW(), NOW()
        WHERE NOT EXISTS (
            SELECT 1 FROM res_currency WHERE name = 'VES'
        )
    """)

def post_init_hook(env):
    """Post-initialization hook - Odoo 17 compatible"""
    # En Odoo 17, el hook recibe env directamente
    
    # Create default webhook configuration if not exists
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

def uninstall_hook(env):
    """Uninstall hook - cleanup - Odoo 17 compatible"""
    # En Odoo 17, el hook recibe env directamente
    
    # Remove configuration parameters
    IrConfigParam = env['ir.config_parameter'].sudo()
    params_to_delete = [
        'tesote.api_token',
        'tesote.api_url',
        'tesote.auto_sync',
        'tesote.sync_days',
        'tesote.webhook_enabled'
    ]
    for param in params_to_delete:
        IrConfigParam.search([('key', '=', param)]).unlink()
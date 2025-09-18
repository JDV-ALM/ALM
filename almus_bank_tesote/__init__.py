from . import models

def pre_init_hook(cr):
    """
    Hook ejecutado antes de instalar el módulo
    Útil para verificar dependencias o preparar datos
    """
    pass


def post_init_hook(cr, registry):
    """
    Hook ejecutado después de instalar el módulo
    Útil para configuración inicial o migración de datos
    """
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Crear configuración por defecto si no existe
    Config = env['tesote.config']
    for company in env['res.company'].search([]):
        existing = Config.search([('company_id', '=', company.id)])
        if not existing:
            Config.create({
                'company_id': company.id,
                'api_token': '',  # Vacío, debe configurarse
                'auto_sync': True,
                'sync_days': 7,
                'max_transactions': 100,
            })


def uninstall_hook(cr, registry):
    """
    Hook ejecutado al desinstalar el módulo
    Útil para limpiar datos o configuraciones
    """
    pass
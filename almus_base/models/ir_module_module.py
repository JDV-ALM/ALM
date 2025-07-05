from odoo import models, fields, api, _


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'
    
    is_almus_module = fields.Boolean(
        string='Módulo Almus',
        default=False,
        help='Indica si es un módulo desarrollado por Almus Dev'
    )
    
    almus_app_config_id = fields.One2many(
        'almus.app.config',
        'module_id',
        string='Configuración de Aplicación'
    )
    
    @api.model
    def _get_almus_modules(self):
        """Identificar módulos Almus por prefijo o autor"""
        # Buscar módulos con prefijos específicos
        almus_prefixes = ['almus_', 'l10n_ve_almus_']
        domain = ['|'] * (len(almus_prefixes) - 1)
        for prefix in almus_prefixes:
            domain.append(('name', '=like', prefix + '%'))
        
        # También buscar por autor
        domain.insert(0, '|')
        domain.append(('author', 'ilike', 'Almus Dev'))
        
        return self.search(domain)
    
    @api.model
    def update_list(self):
        """Sobrescribir para marcar módulos Almus automáticamente"""
        res = super(IrModuleModule, self).update_list()
        
        # Marcar módulos Almus
        almus_modules = self._get_almus_modules()
        almus_modules.write({'is_almus_module': True})
        
        return res
    
    def button_immediate_install(self):
        """Sobrescribir para crear configuración de app si es necesario"""
        res = super(IrModuleModule, self).button_immediate_install()
        
        for module in self.filtered(lambda m: m.is_almus_module and m.state == 'installed'):
            # Verificar si ya tiene configuración
            if not module.almus_app_config_id:
                # Intentar crear configuración automática
                self._create_app_config(module)
        
        return res
    
    def _create_app_config(self, module):
        """Crear configuración de aplicación Almus automáticamente"""
        # Solo crear si el módulo tiene ciertas características
        if not module.application or module.name == 'almus_base':
            return
        
        # Mapear categorías de Odoo a categorías Almus
        category_mapping = {
            'Accounting': 'accounting',
            'Sales': 'sales',
            'Purchases': 'purchase',
            'Inventory': 'inventory',
            'Human Resources': 'hr',
            'Manufacturing': 'manufacturing',
            'Website': 'website',
            'Project': 'project',
        }
        
        almus_category = 'other'
        for odoo_cat, almus_cat in category_mapping.items():
            if odoo_cat in (module.category_id.name or ''):
                almus_category = almus_cat
                break
        
        # Crear configuración
        self.env['almus.app.config'].create({
            'name': module.name.replace('almus_', ''),
            'display_name': module.shortdesc or module.name,
            'module_id': module.id,
            'description': module.summary or module.description,
            'category': almus_category,
            'sequence': 50,
            'is_enabled': False,  # Deshabilitado por defecto
        })
    
    @api.model
    def _update_almus_dependencies(self):
        """Actualizar dependencias entre aplicaciones Almus"""
        almus_apps = self.env['almus.app.config'].search([])
        
        for app in almus_apps:
            if not app.module_id:
                continue
                
            # Obtener dependencias del módulo
            dependencies = app.module_id.dependencies_id
            dep_modules = dependencies.mapped('depend_id')
            
            # Filtrar solo dependencias que son apps Almus
            dep_apps = almus_apps.filtered(
                lambda a: a.module_id in dep_modules
            )
            
            # Actualizar relación
            app.depends_on = [(6, 0, dep_apps.ids)]
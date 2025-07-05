from odoo import models, api

class AlmusFeatureMixin(models.AbstractModel):
    _name = 'almus.feature.mixin'
    _description = 'Mixin para verificar features Almus'
    
    @api.model
    def _almus_feature_enabled(self, feature_name):
        """Verificar si una feature específica está habilitada"""
        return self.env['almus.app.config'].search_count([
            ('name', '=', feature_name),
            ('is_enabled', '=', True),
            '|',
            ('company_ids', '=', False),
            ('company_ids', 'in', [self.env.company.id])
        ]) > 0
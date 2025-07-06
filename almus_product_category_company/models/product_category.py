from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        index=True,
        help="Dejar vacío para compartir entre todas las empresas"
    )
    
    @api.model
    def _is_feature_enabled(self):
        """Verificar si la funcionalidad está habilitada"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'almus_product_category_company.enabled', 'False'
        ) == 'True'
    
    @api.model_create_multi
    def create(self, vals_list):
        """Asignar empresa automáticamente si la funcionalidad está habilitada"""
        if self._is_feature_enabled():
            for vals in vals_list:
                if 'company_id' not in vals:
                    vals['company_id'] = self.env.company.id
        return super().create(vals_list)
    
    @api.constrains('parent_id', 'company_id')
    def _check_parent_company(self):
        """Validar que la categoría padre pertenezca a la misma empresa"""
        if not self._is_feature_enabled():
            return
            
        for category in self:
            if category.parent_id and category.company_id != category.parent_id.company_id:
                raise ValidationError(_(
                    'La categoría padre debe pertenecer a la misma empresa.'
                ))
    
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """Override search para asegurar filtrado por empresa cuando está habilitado"""
        # Si la funcionalidad no está habilitada, comportamiento estándar
        if not self._is_feature_enabled():
            return super()._search(domain, offset, limit, order)
            
        # Si se quiere bypassear el filtro o es superusuario
        if self._context.get('bypass_company_filter') or self.env.su:
            return super()._search(domain, offset, limit, order)
        
        # Verificar si ya hay un filtro de company_id en el dominio
        has_company_filter = any(
            isinstance(term, (list, tuple)) and len(term) >= 3 and term[0] == 'company_id'
            for term in domain
        )
        
        # Agregar filtro de empresa si no existe
        if not has_company_filter:
            domain = ['|', ('company_id', '=', False), ('company_id', 'in', self.env.companies.ids)] + domain
            
        return super()._search(domain, offset, limit, order)
    
    def _compute_display_name(self):
        """Agregar empresa al nombre si está en contexto multi-empresa"""
        super()._compute_display_name()
        
        # Solo si la funcionalidad está habilitada y es multi-empresa
        if (self._is_feature_enabled() and 
            self.env.user.has_group('base.group_multi_company') and
            len(self.env.companies) > 1):
            
            for category in self:
                if category.company_id:
                    category.display_name = f"{category.display_name} [{category.company_id.name}]"
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'almus.feature.mixin']
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        index=True,
        help="Dejar vacío para compartir entre todas las empresas"
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Asignar empresa automáticamente si la funcionalidad está habilitada"""
        if self._almus_feature_enabled('product_category_company'):
            for vals in vals_list:
                if 'company_id' not in vals:
                    vals['company_id'] = self.env.company.id
        return super().create(vals_list)
    
    @api.constrains('parent_id', 'company_id')
    def _check_parent_company(self):
        """Validar que la categoría padre pertenezca a la misma empresa"""
        if not self._almus_feature_enabled('product_category_company'):
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
        if not self._almus_feature_enabled('product_category_company'):
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
    
    def _get_display_name(self, options):
        """Agregar empresa al nombre si está en contexto multi-empresa"""
        name = super()._get_display_name(options)
        
        # Solo si la funcionalidad está habilitada y es multi-empresa
        if (self._almus_feature_enabled('product_category_company') and 
            self.env.user.has_group('base.group_multi_company') and
            self.company_id and
            len(self.env.companies) > 1):
            name = f"{name} [{self.company_id.name}]"
            
        return name
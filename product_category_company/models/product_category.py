from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company,
        help="Empresa a la que esta categoria pertenece"
    )
    
    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """Override search to ensure company filtering is always applied"""
        if self._context.get('bypass_company_filter'):
            return super()._search(domain, offset, limit, order)
        
        # Add company filter if not already in domain
        has_company_filter = any(
            isinstance(term, (list, tuple)) and len(term) >= 3 and term[0] == 'company_id'
            for term in domain
        )
        
        if not has_company_filter and not self.env.su:
            domain = [('company_id', 'in', self.env.companies.ids)] + domain
            
        return super()._search(domain, offset, limit, order)
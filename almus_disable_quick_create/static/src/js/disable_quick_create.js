/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { session } from "@web/session";

patch(Many2OneField.prototype, {
    async willStart() {
        await super.willStart(...arguments);
        
        // Solo aplicar en modelos específicos
        const affectedModels = ['sale.order', 'sale.order.line', 'purchase.order', 'purchase.order.line', 'account.move', 'account.move.line'];
        
        if (!affectedModels.includes(this.env.model.root.resModel)) {
            return;
        }
        
        // Obtener configuraciones del sistema
        const params = await this.env.services.rpc({
            model: 'ir.config_parameter',
            method: 'search_read',
            domain: [['key', 'in', [
                'almus_disable_quick_create.disable_partner_quick_create',
                'almus_disable_quick_create.disable_partner_create_edit',
                'almus_disable_quick_create.disable_product_quick_create',
                'almus_disable_quick_create.disable_product_create_edit'
            ]]],
            fields: ['key', 'value'],
        });
        
        const config = {};
        params.forEach(param => {
            config[param.key] = param.value === 'True';
        });
        
        // Aplicar configuraciones según el campo
        const fieldName = this.props.name;
        const partnerFields = ['partner_id', 'partner_invoice_id', 'partner_shipping_id'];
        const productFields = ['product_id', 'product_template_id'];
        
        if (partnerFields.includes(fieldName)) {
            if (config['almus_disable_quick_create.disable_partner_quick_create']) {
                this.props.canCreate = false;
                this.props.canQuickCreate = false;
            }
            if (config['almus_disable_quick_create.disable_partner_create_edit']) {
                this.props.canCreateEdit = false;
            }
        } else if (productFields.includes(fieldName)) {
            if (config['almus_disable_quick_create.disable_product_quick_create']) {
                this.props.canCreate = false;
                this.props.canQuickCreate = false;
            }
            if (config['almus_disable_quick_create.disable_product_create_edit']) {
                this.props.canCreateEdit = false;
            }
        }
    }
});
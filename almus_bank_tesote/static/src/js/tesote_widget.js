/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class TesoteWidget extends Component {
    static template = "almus_bank_tesote.TesoteWidget";
    static props = ["*"];

    setup() {
        // Widget initialization
    }

    async onTestConnection() {
        // Test connection functionality
        const result = await this.env.services.rpc("/web/dataset/call_kw", {
            model: "res.config.settings",
            method: "action_test_tesote_connection",
            args: [],
            kwargs: {},
        });
        
        if (result) {
            this.env.services.notification.add("Connection test completed", {
                type: "info",
            });
        }
    }
}

registry.category("view_widgets").add("tesote_widget", TesoteWidget);

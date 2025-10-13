/** @odoo-module **/

import { registry } from "@web/core/registry";
import { BaseOptionComponent } from "@website/editor/js/editor/snippets.options";

export class CustomHeaderOption extends BaseOptionComponent {
    static template = "custom_product_detail.CustomHeaderOption";

    async onClickCustomHeader1() {
        // Apply the custom header view dynamically
        await this.customizeWebsite.apply({
            viewKey: "custom_product_detail.custom_as_header_1",
            variable: "as_header1",
        });
    }
}

// Register our new option plugin
registry.category("options").add("custom_header_option", CustomHeaderOption);
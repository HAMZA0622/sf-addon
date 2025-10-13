/** @odoo-module **/

import {WebsiteSale} from '@website_sale/js/website_sale';
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.ExpandAttributeWidget = publicWidget.Widget.extend({
        selector: '.js-expand-btn',
        events: {
            'click': '_onExpandClick',
        },

        /**
         * Click event handler for the Expand button
         * @param {Event} ev
         */
        _onExpandClick: function (ev) {
            ev.preventDefault();
            let $currentTarget = $(ev.currentTarget);
            const allItems = $currentTarget.closest('.variant_attribute ').find('.custom-label-div');

            const hiddenItems = allItems.filter('.custom-display-none-att');

            if (hiddenItems.length > 0) {
                // If there are hidden items, show them
                hiddenItems.removeClass('custom-display-none-att');
            } else {
                // If all items are visible, hide them
                allItems.addClass('custom-display-none-att');
            }
        },
    });


publicWidget.registry.CustomWebsiteSale = publicWidget.Widget.extend({
    selector: '#custom_product_details',
    events: {
        'change .js_custom_variant_change': 'onCustomChangeVariant',
    },
    onCustomChangeVariant: function (ev) {
        let $currentTarget = $(ev.currentTarget);
        let name = $currentTarget.attr('name')
        let value_id = $currentTarget.val();
        if (name && value_id && $('.js_variant_change').length) {
            $('.js_variant_change[name="' + name + '"]').map(function (index, element) {
                if (element.tagName === "SELECT") {
                    $(element).val(value_id);
                    $(element).trigger('change');
                } else {
                    if ($(element).val() == value_id) {
                        if (element.tagName === "INPUT") {
                            $(element).prop('checked', true);
                            
                        } else if (element.tagName === "OPTION") {
                            $(element).prop('selected', true);
                        }
                        $(element).trigger('change');
                    }
                }

                
            }
            );
        }
    },
})

publicWidget.registry.WebsiteSale.include({
    /**
     * @override
     */
    _applyHash: function ($parent) {
        this._super.apply(this, arguments);
        const params = new URLSearchParams(window.location.hash.substring(1));
        if (params.get("attribute_values")) {
            const customAttributeValueIds = params.get("attribute_values").split(',');
            const customInputs =  document.querySelectorAll(
                'input.js_custom_variant_change, select.js_custom_variant_change option'
            );
            customInputs.forEach((element) => {
                if (customAttributeValueIds.includes(element.dataset.attributeValueId)) {
                    if (element.tagName === "INPUT") {
                        element.checked = true;
                    } else if (element.tagName === "OPTION") {
                        element.selected = true;
                    }
                }
            });
            ['.css_custom_attribute_color', '.o_variant_pills'].forEach((selector) => {
                $(selector).removeClass("active").filter(":has(input:checked)").addClass("active");
            });
        }
    }
});

// export default WebsiteSale;

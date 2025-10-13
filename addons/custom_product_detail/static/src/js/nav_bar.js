/** @odoo-module */

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.NavbarProductMenu = publicWidget.Widget.extend({
    selector: '#o_main_nav',

    events: {
        'mouseenter #top_menu li.nav-item.custom-dropdown-toggle': '_onMouseEnterMenu',
        'mouseleave #top_menu li.nav-item.custom-dropdown-toggle': '_onMouseLeaveMenu',
    },

    start() {
        var self = this;
        this.$el.find('#top_menu > li').each(function () {
            const $link = $(this).find('> a');
            if ($(this).find('.dropdown-menu').length > 0) {
                if (!$link.hasClass('dropdown-toggle')) {
                    $link.closest('li').addClass('custom-dropdown-toggle');
                    $link.find('> span').append(' <i class="fa fa-chevron-down dropdown-menu-icon"></i>');
                }
            }
        });
        return this._super(...arguments);
    },
    

    _onMouseEnterMenu: function (event) {
        var dropdown_menu = $(event.currentTarget).find('.dropdown-menu');
        if (dropdown_menu.length > 0) {
            dropdown_menu.css('display', 'block');
        }
    },

    _onMouseLeaveMenu: function (event) {
        var dropdown_menu = $(event.currentTarget).find('.dropdown-menu');
        if (dropdown_menu.length > 0) {
            dropdown_menu.css('display', 'none');
        }
    },
});

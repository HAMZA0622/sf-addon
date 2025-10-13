/** @odoo-module */

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.ProductImageSlideshow = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    events: {
        'click .image-plus': '_onClickSearchPlusIcon',
    },

    start() {
        debugger
        if (!Array.isArray(this.options.dataSource)) {
            this.options.dataSource = [];
            this.options.index = 0;
            this.options.showHideAnimationType= 'none';
        }
        var $img = this.$el.find('img.custom-att-image.image-plus');
        var self = this;
        if ($img.length) {
            $img.each((i, el) => {
                var img = $(el);
                img.attr('data-index', self.options.index);
                self.options.index += 1;
                var src = img.attr('src').replace('image_512', 'image_1024');
                var width = img[0].naturalWidth;
                var height = img[0].naturalHeight;  
                var newHeight = 750;
                var newWidth = (newHeight * width) / height;
                var alt = img.attr('alt') || 'Product image';
                if (newWidth > 700 || isNaN(newWidth)) {
                    newWidth = 700;
                }
                console.log('newWidth', newWidth);
                self.options.dataSource.push({
                    src: src,
                    width: newWidth,
                    height: newHeight,
                    alt: alt,
                });
            
            });
           
        }
        return this._super(...arguments);
    },
    
    

    _onClickSearchPlusIcon: function (event) {
        this.options.index = parseInt($(event.currentTarget).attr('data-index')); 
        const pswp = new PhotoSwipe(this.options);
        pswp.init(); 
    },
});

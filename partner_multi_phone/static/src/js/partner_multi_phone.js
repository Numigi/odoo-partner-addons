odoo.define('partner_multi_phone', function (require) {
"use strict";

var PhoneExtension = require('web.basic_fields').FieldChar.extend({

    className: "o_phone_extension",

    _renderReadonly: function () {
        this._super.apply(this, arguments);
        var label = $('<span>', {class: "o_phone_extension__label", text: "Ext: "});
        this.$el.prepend(label);
    },
});

require('web.field_registry').add('phone_extension', PhoneExtension)

});

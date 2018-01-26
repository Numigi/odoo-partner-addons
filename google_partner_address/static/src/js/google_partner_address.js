/*
    © 2017 Savoir-faire Linux <https://savoirfairelinux.com>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/
odoo.define('google_partner_address', function (require) {
    "use strict";

    var core = require('web.core');
    var common = require('web.form_common'); 
    var Model = require('web.DataModel');
    var _t = core._t;

    var country_deferred = $.Deferred();
    var state_deferred = $.Deferred();
    var countries = {};
    var states = {};

    new Model('res.country.state').query(['id', 'code', 'country_id']).all().then(
        function(result) {
            result.forEach(function(state){
                if (!states[state.code]){
                    states[state.code] = {}
                }

                states[state.code][state.country_id[0]] = {
                    'state_id': state.id};
            })
            state_deferred.resolve();
        });

    new Model('ir.model.data').call('search_read', [
        [['model', '=', 'res.country'], ['module', '=', 'base']],
        ['res_id', 'name'],
    ]).then(function(result) {
        result.forEach(function(country){
            countries[country.res_id] = country.name;
        })
        country_deferred.resolve();
    });

    var AddressWidget = common.FormWidget.extend({
        template: "AddressField",
        init: function(field_manager, node) {
            this._super.apply(this, arguments);    
            this.placeholder = _t("Indicate a place...");
        },
        start: function() {
            this.input = this.$('.o_address_input')

            this.autocomplete = new google.maps.places.Autocomplete(this.input[0]);
            this.autocompleteService = new google.maps.places.AutocompleteService();
            this.placesService = new google.maps.places.PlacesService($('<div></div>')[0]);
            this.restrictions = {};
            this.set_country_boundries();
            
            var self = this;
            this.field_manager.on("load_record", this, function() {
                self.input.val('');
            });
            this.autocomplete.addListener('place_changed', function() {
                self.onchange_place();
            });

            this.on("change:effective_readonly", this, this.onchange_effective_readonly);
            this.field_manager.on("field_changed:type", this, this.check_widget_visibility);
            this.field_manager.on("field_changed:parent_id", this, this.check_widget_visibility);
            this.field_manager.on("field_changed:country_id", this, this.set_country_boundries);
            this.field_manager.on("field_changed:zip", this, this.set_zipcode_boundries);

            this.onchange_effective_readonly();
        },
        check_widget_visibility: function() {
            var type = this.field_manager.fields.type;
            if (typeof type !== 'undefined') {
                type = type.get_value();
            } else {
                type = false;
            }

            var parent_id = this.field_manager.fields.parent_id;
            if (typeof parent_id !== 'undefined') {
                parent_id = parent_id.get_value();
            } else {
                parent_id = false;
            }

            if (type === 'contact' && parent_id !== false) {
                this.input.hide();
            } else {
                this.input.show();
            }
        },
        onchange_effective_readonly: function() {
            if (this.get('effective_readonly')) {
                this.input.hide();
            } else {
                this.check_widget_visibility();
            } 
        },
        onchange_place: function() {            
            var place = this.autocomplete.getPlace();
            var address = {};
            var fields = this.field_manager.fields;

            for (var i = 0; i < place.address_components.length; i++) {
                var addressType = place.address_components[i].types[0];
                if (addressType === "route") {
                    address[addressType] = place.address_components[i].long_name;
                } else {
                    address[addressType] = place.address_components[i].short_name;
                }
            }

            this.set_street(address);
            this.set_city(address);
            var country_id = this.set_country(address["country"]);
            this.set_state(address, country_id);
            this.set_postal_code(address);
        },
        set_street: function(address) {
            var address_parts = [];
            if (address["street_number"]) {
                address_parts.push(address["street_number"]);
            }
            if (address["route"]) {
                address_parts.push(address["route"]);
            }

            var street = address_parts.join(' ');
            this.field_manager.fields.street.set_value(street);
        },
        set_city: function(address) {
            var city = (
                address["locality"] ||
                address["administrative_area_level_2"] ||
                address["administrative_area_level_1"]);
            this.field_manager.fields.city.set_value(city);
        },
        get_country_id: function(country_code) {
            var key;
            for (key in countries) {
                if (countries[key] == country_code) {
                    return parseInt(key);
                }
            }
        },
        set_country: function(country) {
            var country_id = this.field_manager.fields.country_id.get_value();
            if (!country_id){
                var country_code = country.toLowerCase();
                country_id = this.get_country_id(country_code);
            }
            this.field_manager.fields.country_id.set_value(country_id);
            return country_id;
        },
        set_state: function(address, country_id) {
            var areas = [];
            var key;
            var state_code ;

            if (address["administrative_area_level_1"]) {
                areas = areas.concat(address["administrative_area_level_1"]);
            }
            if (address["administrative_area_level_2"]) {
                areas = areas.concat(address["administrative_area_level_2"]);
            }

            for (key in areas) {
                if (states[areas[key]]) {
                    state_code = areas[key];
                    continue;
                }
            }

            if (state_code) {    
                var state_id = states[state_code][country_id]['state_id'] || null;
                this.field_manager.fields.state_id.set_value(state_id);
            } else {
                this.field_manager.fields.state_id.set_value(null);
            }
        },
        set_postal_code: function(address) {
            var postal_code = '';
            if (address["postal_code_prefix"]){
                postal_code = address["postal_code_prefix"];
            }
            if (address["postal_code"]) {
                postal_code = address["postal_code"];
            }
            if (address["postal_code_suffix"]){
                postal_code = postal_code + ' ' + address["postal_code_suffix"];
            }
            this.field_manager.fields.zip.set_value(postal_code) 
        },
        set_country_boundries: function() {
            var country_id = this.field_manager.fields.country_id.get_value();
            if (country_id) {
                var country_code = countries[country_id] || null;
                this.restrictions = {country: country_code};
                this.autocomplete.setComponentRestrictions(this.restrictions);
            } else {
                this.autocomplete.setComponentRestrictions({'country': []});
            }
        },
        set_zipcode_boundries: function() {
            var zipCode = this.field_manager.fields.zip.get_value();
            
            if (zipCode) {
                var request = {
                    input: zipCode,
                    types: ['geocode'],
                    componentRestrictions: this.restrictions
                };
                var self = this;
                self.autocompleteService.getPlacePredictions(request, function(preds) {
                    var place = (preds && preds[0]) || null;
                    if (place) {
                        var request = {
                            placeId: place.place_id
                        };
                        self.placesService.getDetails(request, function(details) {
                            /*
                            details.geometry contains information related to
                            the geometric properties of the place, viewport
                            defines the bounds of the map related to the zip code.
                            */
                            if (details && details.geometry && details.geometry.viewport) {
                                // Modify the search area on the autocomplete object
                                self.autocomplete.setBounds(details.geometry.viewport);
                            }
                        });
                    }
                });
            } else {
                this.autocomplete.setBounds();
            }
        }
    });

    core.form_custom_registry.add('google_partner_address', AddressWidget);

    return {
        AddressWidget: AddressWidget,
    };

});

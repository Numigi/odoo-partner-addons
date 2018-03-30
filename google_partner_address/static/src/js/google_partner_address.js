/*
    © 2017-2018 Savoir-faire Linux <https://www.savoirfairelinux.com>
    © 2018 Numigi <https://www.numigi.com>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL.html).
*/
odoo.define("google_partner_address", function (require) {
"use strict";

var AbstractField = require("web.AbstractField");
var registry = require("web.field_registry");

var rpc = require("web.rpc");
var Class = require('web.Class');

var CountryRegistry = Class.extend({
    init() {
        this._countriesById = {};
        this._countriesByCode = {};
        this._statesByCountry = {};
        this._statesById = {};
        this._fetchCountries();
        this._fetchStates();
    },
    /**
     * Fetch country codes from the server.
     */
    _fetchCountries(){
        var self = this;
        rpc.query({
            model: "res.country",
            method: "search_read",
            args:[[], ["id", "code"]],
        }).then(function(result) {
            result.forEach(function(el){
                var code = el.code.toLowerCase();
                self._countriesById[el.id] = code;
                self._countriesByCode[code] = el.id;
            })
        });
    },
    /**
     * Fetch state codes from the server.
     */
    _fetchStates(){
        var self = this;
        rpc.query({
            model: "res.country.state",
            method: "search_read",
            args:[[], ["id", "code", "country_id"]],
        }).then(function(result) {
            result.forEach(function(el){
                var countryId = el.country_id[0];
                var code = el.code.toLowerCase();
                if (!self._statesByCountry[countryId]){
                    self._statesByCountry[countryId] = {}
                }
                self._statesByCountry[countryId][code] = el.id;
                self._statesById[el.id] = [countryId, code];
            });
        });
    },
    /**
     * Get the code of a country.
     * @param {number} countryId - the id of the country
     * @returns {string} the country code
     */
    getCountryCode(countryId){
        if(!this._countriesById[countryId]){
            throw new Error('No country registered with the id ' + countryId + '.');
        }
        return this._countriesById[countryId];
    },
    /**
     * Get the id of a country.
     * @param {string} countryCode - the code of a country
     * @returns {number} the country id
     */
    getCountryId: function(countryCode) {
        if(!this._countriesByCode[countryCode]){
            throw new Error('No country registered with the code ' + countryCode + '.');
        }
        return this._countriesByCode[countryCode];
    },
    /**
     * Get the code of a state.
     * @param {number} stateId - the id of a country
     * @returns {string} the state code
     */
    getStateCode(stateId){
        if(!this._statesById[stateId]){
            throw new Error('No country state registered with the id ' + stateId + '.');
        }
        return this._statesById[stateId];
    },
    /**
     * Get the id of a state.
     * @param {string} countryCode - the code of a state
     * @returns {number} the state id
     */
    getStateId: function(countryCode, stateCode) {
        var countryId = this.getCountryId(countryCode);
        var states = this._statesByCountry[countryId];
        if(!states || !states[stateCode]){
            return null;
        }
        return states[stateCode];
    },
});

var countryRegistry = new CountryRegistry();


/**
 * A class responsible for fetching the address from a place autocomplete widget.
 */
var PlaceAutocompleteProxy = Class.extend({
    /**
     * Initialize the autocomplete proxy.
     *
     * @param {google.maps.places.Autocomplete} autocomplete
     */
    init(autocomplete){
        this._autocomplete = autocomplete;
        this._address = {};
        this._fetchPlaces();
    },
    /**
     * Fetch the places from the autocomplete
     */
    _fetchPlaces(){
        var place = this._autocomplete.getPlace();
        for (var i = 0; i < place.address_components.length; i++) {
            var addressType = place.address_components[i].types[0];
            if (addressType === "route") {
                this._address[addressType] = place.address_components[i].long_name;
            } else {
                this._address[addressType] = place.address_components[i].short_name;
            }
        }
    },
    /**
     * Get the value for the street field.
     * @returns {string | null}
     */
    getStreet(){
        var streetParts = [];
        if(this._address.street_number){
            streetParts.push(this._address.street_number);
        }
        if(this._address.route){
            streetParts.push(this._address.route);
        }
        return streetParts.join(" ");
    },
    /**
     * Get the value for the city field.
     * @returns {string | null}
     */
    getCity(){
        return this._address.locality || null;
    },
    /**
     * Get the code of the country.
     * @returns {string | null}
     */
    getCountryCode(){
        var code = this._address.country;
        return code ? code.toLowerCase() : null;
    },
    /**
     * Get the code of the country state.
     * @returns {string | null}
     */
    getStateCode(){
        var code = this._address.administrative_area_level_1;
        return code ? code.toLowerCase() : null;
    },
    /**
     * Get the zip code.
     * @returns {string | null}
     */
    getZip(){
        var countryCode = this.getCountryCode();
        if(countryCode === "us"){
            return this._getZipUS();
        }
        return this._address.postal_code || null;
    },
    /**
     * Get the zip code for an address in the United States.
     * @returns {string | null}
     */
    _getZipUS(){
        var zip = this._address.postal_code;
        if(zip){
            var suffix = this._address.postal_code_suffix;
            if(suffix){
                zip = zip.concat("-").concat(suffix);
            }
        }
        return zip || null;
    },
});


/**
 * A class responsible for setting the boundaries on a place autocomplete widget.
 */
var PlaceBoundaryProxy = Class.extend({
    /**
     * Init the place boundaries proxy.
     *
     * @param {google.maps.places.Autocomplete} autocomplete
     * @param {google.maps.places.AutocompleteService} autocompleteService
     * @param {google.maps.places.PlacesService} placesService
     */
    init(autocomplete, autocompleteService, placesService){
        this._autocomplete = autocomplete;
        this._autocompleteService = autocompleteService;
        this._placesService = placesService;
    },
    /**
     * Set the zip code boundaries on the autocomplete.
     */
    setBoundaries(countryCode, zipCode) {
        if(zipCode){
            var request = {
                input: zipCode,
                types: ["geocode"],
                componentRestrictions: {country: countryCode || []},
            };

            var self = this;
            self._autocompleteService.getPlacePredictions(request, function(predictions) {
                if (predictions) {
                    self._setGeometryBoundaries(predictions[0]);
                }
            });
        }
        else{
            var restrictions = {country: countryCode || []};
            this._autocomplete.setComponentRestrictions(restrictions);
            this._autocomplete.setBounds();
        }
    },
    /**
     * Set the geometry boundaries for a given place on the autocomplete.
     *
     * @param {Object} place - the details of the place
     */
    _setGeometryBoundaries(place){
        var self = this;
        var request = {placeId: place.place_id};
        this._placesService.getDetails(request, function(details) {
            if (details && details.geometry && details.geometry.viewport) {
                self._autocomplete.setBounds(details.geometry.viewport);
            }
        });
    },
});


var AddressWidget = AbstractField.extend({
    tagName: "input",
    init(parent, name, record, options) {
        this._super.apply(this, arguments);
    },
    start() {
        this._super.apply(this, arguments);
        this.input = this.$el
        this._autocomplete = new google.maps.places.Autocomplete(this.input[0]);
        this._autocompleteService = new google.maps.places.AutocompleteService();
        this._placesService = new google.maps.places.PlacesService($("<div></div>")[0]);
        var self = this;
        setTimeout(function(){
            self._setupFieldListeners();
            self._setBoundaries();
        }, 0);
    },
    _renderEdit() {
        var input = this.$el || $("<input/>");
        input.addClass("o_input");
        input.attr({type: "text"});
        input.val(this._formatValue(this.value));

        // Setting this attribute is required for the widget to be focusable with tabindex.
        this.$input = input;

        return input;
    },
    getFocusableElement() {
        /*
        An abstract field by default can not be selected when we press tab on
        the previous input.
        This allows to select the input "place" to facilitate the navigation between 
        the address fields.
        */
        return this.$input || $();
    },
    /**
     * Add onchange listeners to form fields.
     */
    _setupFieldListeners() {
        var self = this;
        var countryField = self._getFieldByName("country_id");
        countryField.on("field_changed", self, self._setBoundaries);

        var zipField = self._getFieldByName("zip");
        zipField.on("field_changed", self, self._setBoundaries);

        self._autocomplete.addListener("place_changed", function() {
            self._updateAddressFromAutocomplete();
        });
    },
    /**
     * Fill the fields of the partner form from the selected place.
     */
    _updateAddressFromAutocomplete() {
        var proxy = new PlaceAutocompleteProxy(this._autocomplete);
        this.trigger("input");

        this._setInputValue("street", proxy.getStreet());
        this._setInputValue("city", proxy.getCity());
        this._setInputValue("zip", proxy.getZip());

        var countryCode = proxy.getCountryCode();
        if (countryCode){
            var countryId = countryRegistry.getCountryId(countryCode);
            this._setMany2oneValue("country_id", countryId);
        }

        var stateCode = proxy.getStateCode();
        if(countryCode && stateCode){
            var stateId = countryRegistry.getStateId(countryCode, stateCode);
            this._setMany2oneValue("state_id", stateId);
        }
    },
    /**
     * Get a field from the partner form.
     *
     * Throw an error if the field does not exist.
     *
     * @param {string} field_name - The name of the field
     * @returns {web.AbstractField}
     */
    _getFieldByName: function(field_name) {
        var form = this.getParent();
        var field = form.allFieldWidgets[form.state.id].find(function(field){return field.name === field_name});
        if(!field){
            throw new Error('The field ' + field_name + ' is not registered inside the form view.');
        }
        return field;
    },
    /**
     * Set the value of an input field on the form view.
     *
     * @param {string} field_name - the name of the field
     * @param {string} value - the value to set
     */
    _setInputValue(field_name, value){
        var field = this._getFieldByName(field_name);
        field.$input.val(value).trigger("input");
    },
    /**
     * Get the value of a field from the form view.
     *
     * @param {string} field_name - the name of the field
     * @returns {string} the input value
     */
    _getFieldValue(field_name){
        var field = this._getFieldByName(field_name);
        return field.lastSetValue !== undefined ? field.lastSetValue : field.value;
    },
    /**
     * Get the value of a field from the form view.
     *
     * @param {string} field_name - the name of the field
     * @returns {string} the input value
     */
    _getMany2oneFieldValue(field_name){
        var field = this._getFieldByName(field_name);
        var value = field.lastSetValue !== undefined ? field.lastSetValue : field.value;
        if(typeof(value) === "number"){
            return value;
        }
        else if(value && value.res_id){
            return value.res_id;
        }
        else if(value && value.id){
            return value.id;
        }
        else{
            return null;
        }
    },
    /**
     * Get the zip code from the partner form.
     * @returns {string} the zip code
     */
    _getZipCode(){
        return this._getFieldValue('zip');
    },
    /**
     * Get the country code from the partner form.
     * @returns {string} the country code
     */
    _getCountryCode(){
        var countryId = this._getMany2oneFieldValue('country_id');
        return countryId ? countryRegistry.getCountryCode(countryId) : null; 
    },
    /**
     * Set the value of an many2one field on the form view.
     *
     * @param {string} field_name - the name of the field
     * @param {string} value - the id of the foreign record.
     */
    _setMany2oneValue(field_name, value){
        var field = this._getFieldByName(field_name);
        field.reinitialize(value || null);
    },
    /**
     * Set the zip boundaries on the place autocomplete widget.
     */
    _setBoundaries() {
        var countryCode = this._getCountryCode();
        var zip = this._getZipCode();
        var proxy = new PlaceBoundaryProxy(
            this._autocomplete, this._autocompleteService, this._placesService);
        proxy.setBoundaries(countryCode, zip);
    },
});

registry.add("google_partner_address", AddressWidget);

return {
    countryRegistry,
    PlaceAutocompleteProxy,
    PlaceBoundaryProxy,
    AddressWidget,
}

});

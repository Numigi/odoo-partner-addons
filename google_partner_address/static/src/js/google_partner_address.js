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
var Class = require("web.Class");

/**
 * Class responsible for converting data about countries and states.
 *
 * The countries/states data is fetched once from the database.
 * Then, it allows external classes to convert ids to country/state codes and vice versa.
 */
var CountryRegistry = Class.extend({
    init() {
        this._countriesById = new Map();
        this._countriesByCode = new Map();
        this._statesByCountry = new Map();
        this._statesById = new Map();

        this._querySent = false;
        this._countriesFetched = new $.Deferred();
        this._statesFetched = new $.Deferred();

        // Deferred that allows external classes to know when all data required by
        // the registry been fetched from the database.
        this.ready = $.when(this._countriesFetched, this._statesFetched);
    },
    /**
     * Fetch data from the server in order to fill the registry.
     */
    fetchData(){
        if(!this._querySent){
            this._fetchCountries();
            this._fetchStates();
            this._querySent = true;
        }
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
                self._countriesById.set(el.id, code);
                self._countriesByCode.set(code, el.id);
            });
            self._countriesFetched.resolve();
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
                if (!self._statesByCountry.get(countryId)){
                    self._statesByCountry.set(countryId, new Map());
                }
                self._statesByCountry.get(countryId).set(code, el.id);
                self._statesById.set(el.id, [countryId, code]);
            });
            self._statesFetched.resolve();
        });
    },
    /**
     * Get the code of a country.
     * @param {number} countryId - the id of the country
     * @returns {string} the country code
     */
    getCountryCode(countryId){
        if(!this._countriesById.get(countryId)){
            throw new Error("No country registered with the id " + countryId + ".");
        }
        return this._countriesById.get(countryId);
    },
    /**
     * Get the id of a country.
     * @param {string} countryCode - the code of a country
     * @returns {number} the country id
     */
    getCountryId(countryCode) {
        if(!this._countriesByCode.get(countryCode)){
            throw new Error("No country registered with the code " + countryCode + ".");
        }
        return this._countriesByCode.get(countryCode);
    },
    /**
     * Get the code of a state.
     * @param {number} stateId - the id of a country
     * @returns {string} the state code
     */
    getStateCode(stateId){
        if(!this._statesById.get(stateId)){
            throw new Error("No country state registered with the id " + stateId + ".");
        }
        return this._statesById.get(stateId);
    },
    /**
     * Get the id of a state.
     * @param {string} countryCode - the code of a state
     * @returns {number} the state id
     */
    getStateId(countryCode, stateCode) {
        var countryId = this.getCountryId(countryCode);
        var states = this._statesByCountry.get(countryId);
        if(!states || !states.get(stateCode)){
            return null;
        }
        return states.get(stateCode);
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
        this._address = new Map();
        this._fetchPlaces();
    },
    /**
     * Fetch the places from the autocomplete
     */
    _fetchPlaces(){
        var place = this._autocomplete.getPlace();
        var self = this;
        place.address_components.forEach(function(component){
            var addressType = component.types[0];
            if (addressType === "route") {
                self._address.set(addressType, component.long_name);
            } else {
                self._address.set(addressType, component.short_name);
            }
        });
    },
    /**
     * Get the value for the street field.
     * @returns {string | null}
     */
    getStreet(){
        var streetParts = [];
        if(this._address.get("street_number")){
            streetParts.push(this._address.get("street_number"));
        }
        if(this._address.get("route")){
            streetParts.push(this._address.get("route"));
        }
        return streetParts.join(" ");
    },
    /**
     * Get the value for the city field.
     * @returns {string | null}
     */
    getCity(){
        return this._address.get("locality") || null;
    },
    /**
     * Get the code of the country.
     * @returns {string | null}
     */
    getCountryCode(){
        var code = this._address.get("country");
        return code ? code.toLowerCase() : null;
    },
    /**
     * Get the code of the country state.
     * @returns {string | null}
     */
    getStateCode(){
        var code = this._address.get("administrative_area_level_1");
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
        return this._address.get("postal_code") || null;
    },
    /**
     * Get the zip code for an address in the United States.
     * @returns {string | null}
     */
    _getZipUS(){
        var zip = this._address.get("postal_code");
        if(zip){
            var suffix = this._address.get("postal_code_suffix");
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
            // The same session token is reused by autocompleteService.getPlacePredictions
            // and placesService.getDetails
            var sessionToken = new google.maps.places.AutocompleteSessionToken();

            var request = {
                input: zipCode,
                types: ["geocode"],
                componentRestrictions: {country: countryCode || []},
                sessionToken: sessionToken,
            };

            var self = this;

            self._autocompleteService.getPlacePredictions(request, function(predictions) {
                if (predictions) {
                    self._setGeometryBoundaries(predictions[0], sessionToken);
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
    _setGeometryBoundaries(place, sessionToken){
        var self = this;
        var request = {
            placeId: place.place_id,
            fields: ['geometry'],
            sessionToken: sessionToken,
        };

        this._placesService.getDetails(request, function(details) {
            if (details && details.geometry && details.geometry.viewport) {
                self._autocomplete.setBounds(details.geometry.viewport);
            }
        });
    },
});


var AddressWidget = AbstractField.extend({
    tagName: "input",
    start() {
        this._super.apply(this, arguments);
        this.input = this.$el;

        this._autocomplete = new google.maps.places.Autocomplete(this.input[0]);

        // Limit fields to address_components only to prevent additional billing per api call.
        this._autocomplete.setFields(['address_components']);

        this._autocompleteService = new google.maps.places.AutocompleteService();
        this._placesService = new google.maps.places.PlacesService($("<div></div>")[0]);

        var self = this;
        setTimeout(function(){
            self._setupFieldListeners();
            self._setBoundaries();
        }, 0);

        countryRegistry.fetchData();
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

        var self = this;

        var countryCode = proxy.getCountryCode();
        if (countryCode){
            countryRegistry.ready.then(function(){
                var countryId = countryRegistry.getCountryId(countryCode);
                self._setMany2oneValue("country_id", countryId);
            });
        }

        var stateCode = proxy.getStateCode();
        if(countryCode && stateCode){
            countryRegistry.ready.then(function(){
                var stateId = countryRegistry.getStateId(countryCode, stateCode);
                self._setMany2oneValue("state_id", stateId);
            });
        }
    },
    /**
     * Get a field from the partner form.
     *
     * Throw an error if the field does not exist.
     *
     * @param {string} fieldName - The name of the field
     * @returns {web.AbstractField}
     */
    _getFieldByName(fieldName) {
        var form = this.getParent();
        var field = form.allFieldWidgets[form.state.id].find(function(field){
            return field.name === fieldName;
        });
        if(!field){
            throw new Error("The field " + fieldName + " is not registered inside the form view.");
        }
        return field;
    },
    /**
     * Set the value of an input field on the form view.
     *
     * @param {string} fieldName - the name of the field
     * @param {string} value - the value to set
     */
    _setInputValue(fieldName, value){
        var field = this._getFieldByName(fieldName);
        field.$input.val(value).trigger("input").trigger("change");
    },
    /**
     * Get the value of a field from the form view.
     *
     * @param {string} fieldName - the name of the field
     * @returns {string} the input value
     */
    _getFieldValue(fieldName){
        var field = this._getFieldByName(fieldName);
        return (typeof field.lastSetValue !== "undefined") ? field.lastSetValue : field.value;
    },
    /**
     * Get the value of a field from the form view.
     *
     * @param {string} fieldName - the name of the field
     * @returns {string} the input value
     */
    _getMany2oneFieldValue(fieldName){
        var field = this._getFieldByName(fieldName);
        var value = (typeof field.lastSetValue !== "undefined") ? field.lastSetValue : field.value;

        // Case where the value stored is a raw record id.
        if(typeof value === "number"){
            return value;
        }

        // Case where the field contains a record.
        // Odoo is inconsistent with many2one records fetched from the server.
        // Sometimes, the record id is contained in the attribute res_id.
        // Sometimes, the record id is contained in the attribute id.
        if(value && value.res_id){
            return value.res_id;
        }
        if(value && value.id){
            return value.id;
        }

        // Case where the field is empty.
        return null;
    },
    /**
     * Set the zip boundaries on the place autocomplete widget.
     */
    _setBoundaries() {
        var self = this;
        countryRegistry.ready.then(function(){
            var countryCode = self._getCountryCode();
            var zip = self._getZipCode();
            var proxy = new PlaceBoundaryProxy(
                self._autocomplete, self._autocompleteService, self._placesService);
            proxy.setBoundaries(countryCode, zip);
        });
    },
    /**
     * Get the zip code from the partner form.
     * @returns {string} the zip code
     */
    _getZipCode(){
        return this._getFieldValue("zip");
    },
    /**
     * Get the country code from the partner form.
     *
     * When calling this method, the country registry must be ready.
     * See attribute `ready` of `.CountryRegistry`
     *
     * @returns {string} the country code
     */
    _getCountryCode(){
        var countryId = this._getMany2oneFieldValue("country_id");
        return countryId ? countryRegistry.getCountryCode(countryId) : null; 
    },
    /**
     * Set the value of an many2one field on the form view.
     *
     * @param {string} fieldName - the name of the field
     * @param {string} value - the id of the foreign record.
     */
    _setMany2oneValue(fieldName, value){
        var field = this._getFieldByName(fieldName);
        field.reinitialize(value || null);
    },
});

registry.add("google_partner_address", AddressWidget);

return {
    countryRegistry,
    PlaceAutocompleteProxy,
    PlaceBoundaryProxy,
    AddressWidget,
};

});

odoo.define('petstore', function(require) {
    'use strict';
    var core = require('web.core')
    var Widget = require('web.Widget');
    var Model = require('web.Model');

    var GreetingWidget = Widget.extend({
        className: 'petstore_greeting',
        start: function() {
            this.$el.append($('<div>').text('We are so happy to see you again in this menu!'));
        },
    });

    var HomePage = Widget.extend({
        template: 'HomePageTemplate',
        className: 'petstore_homepage',
        init: function(parent) {
            this._super(parent);
            this.name = "Mordecai";
        },
        start: function() {
            this.$el.append($('<div>').text('Hello dear Odoo user!'));
            var greeting = new GreetingWidget();
            return greeting.appendTo(this.$el);
            //var self = this;
            //var model = new Model('oepetstore.message_of_the_day');
            //model.call("my_method", {context: new instance.web.CompoundContext()}).then(function(result) {
            //    self.$el.append("<div>Hello " + result["hello"] + "</div>");
        },
    });

    core.action_registry.add('petstore.homepage', HomePage);
})

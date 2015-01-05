///<reference path="jquery.d.ts"/>
///<reference path="underscore.d.ts"/>
///<reference path="backbone.d.ts"/>

// only changed the ///<references path values in backbone.d.ts

import Backbone = require("backbone");

class Animal extends Backbone.Model {

    initialize(attributes: any) {
            this.set('name', 'joe');
    }
}
/// <reference path="../lib/mocha/mocha.d.ts" />
/// <reference path="../lib/chai/chai.d.ts" />
/// <reference path="../lib/sinon/sinon.d.ts" />
/// <reference path="../lib/sinon-chai/sinon-chai.d.ts" />



var expect = chai.expect;

import U = require("../utils/utils");

export var declare = function() {

    describe('Utils tests (TotalBasicUtils)', function(){
        describe('#a()', function(){
            it('should return a', function(){
                expect('a').to.equal(U.TotalBasicUtils.a());
            });
        });
        describe('#b()', function(){
            it('should return b', function(){
                expect('b').to.equal((new U.TotalBasicUtils()).b());
            });
        });


    });
};



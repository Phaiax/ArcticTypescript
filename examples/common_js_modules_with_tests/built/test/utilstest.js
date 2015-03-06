/// <reference path="../lib/mocha/mocha.d.ts" />
/// <reference path="../lib/chai/chai.d.ts" />
/// <reference path="../lib/sinon/sinon.d.ts" />
/// <reference path="../lib/sinon-chai/sinon-chai.d.ts" />
var U = require("../utils/utils");
var chai = require('chai');
var expect = chai.expect;
describe('Array', function () {
    describe('#indexOf()', function () {
        it('should return -1 when the value is not present', function () {
            expect(-1).to.equal([1, 2, 3].indexOf(5));
            expect(-1).to.equal([1, 2, 3].indexOf(0));
        });
    });
});
describe('Utils tests (TotalBasicUtils)', function () {
    describe('#a()', function () {
        it('should return a', function () {
            expect('a').to.equal(U.TotalBasicUtils.a());
        });
    });
    describe('#b()', function () {
        it('should return b', function () {
            expect('b').to.equal((new U.TotalBasicUtils()).b());
        });
    });
});

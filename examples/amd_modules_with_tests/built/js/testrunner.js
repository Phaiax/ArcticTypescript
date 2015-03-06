/// <reference path="lib/mocha/mocha.d.ts" />
/// <reference path="lib/chai/chai.d.ts" />
/// <reference path="lib/sinon-chai/sinon-chai.d.ts" />
define(["require", "exports", 'tests/utilstest'], function (require, exports, utilstest) {
    mocha.setup('bdd');
    utilstest.declare();
    mocha.run();
});
//# sourceMappingURL=testrunner.js.map
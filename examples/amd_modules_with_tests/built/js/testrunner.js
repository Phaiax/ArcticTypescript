define(["require", "exports", './tests/utilstest'], function (require, exports, utilstest) {
    mocha.setup('bdd');
    utilstest.declare();
    mocha.run();
});
//# sourceMappingURL=testrunner.js.map
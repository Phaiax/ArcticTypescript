var Testmodule;
(function (Testmodule) {
    var Test = (function () {
        function Test() {
        }
        Test.prototype.start = function () {
            return this;
        };
        Test.prototype.stop = function () {
            return this;
        };
        return Test;
    })();
    Testmodule.Test = Test;
})(Testmodule || (Testmodule = {}));
/// <reference path="second.ts" />
var second = new Testmodule.Test();
second.start();
second.stop();
//# sourceMappingURL=out.js.map
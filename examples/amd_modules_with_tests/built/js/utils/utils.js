define(["require", "exports"], function (require, exports) {
    var TotalBasicUtils = (function () {
        function TotalBasicUtils() {
        }
        TotalBasicUtils.a = function () {
            console.log("a");
            return "a";
        };
        TotalBasicUtils.prototype.b = function () {
            console.log("b");
            return "c";
        };
        return TotalBasicUtils;
    })();
    exports.TotalBasicUtils = TotalBasicUtils;
});
//# sourceMappingURL=utils.js.map
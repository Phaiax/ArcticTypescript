define(["require", "exports", './utils/utils'], function (require, exports, U) {
    U.TotalBasicUtils.a();
    (new U.TotalBasicUtils()).b();
    setTimeout(function () {
        document.getElementById("dyn").innerHTML = "Dynamic!";
    }, 1000);
});
//# sourceMappingURL=app.js.map
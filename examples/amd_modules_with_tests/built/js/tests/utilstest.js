define(["require", "exports", "../utils/utils"], function (require, exports, U) {
    var expect = chai.expect;
    exports.declare = function () {
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
    };
});
//# sourceMappingURL=utilstest.js.map
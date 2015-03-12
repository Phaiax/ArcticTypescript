
import U = require('./utils/utils');

U.TotalBasicUtils.a();

(new U.TotalBasicUtils()).b();

setTimeout(function(){
	document.getElementById("dyn").innerHTML = "Dynamic!"
}, 1000);

var k = {"abcde" : 22}

console.log(k.abcdefg)
console.log(k.abcdefgh)
console.log(k.abcdefghi)
console.log(k.abcdefghij)

class AClass {

    constructor(argument) {
        // code...
    }

    public test() : void {

    }
}
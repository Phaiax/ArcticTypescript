
import U = require('./utils/utils');

U.TotalBasicUtils.a();

(new U.TotalBasicUtils()).b();

setTimeout(function(){
	document.getElementById("dyn").innerHTML = "Dynamic!"
}, 1000);

var k = {"abcde" : 22}

class AClass {

    constructor(argument) {
        // code...
    }

    public test() : void {
    }
}

import U = require('./utils/utils');

U.TotalBasicUtils.a();

(new U.TotalBasicUtils()).b();

setTimeout(function(){
	document.getElementById("dyn").innerHTML = "Dynamic!"
}, 1000);

var k = 22;

var s = function(){}

var o = () => {}



/// <reference path="card.ts" />

var tartatos = 44;

var sigma = "asdasd";

var bold = tartatos;


setTimeout(function(){
    document.getElementById("dyn").innerHTML = "Dynamic!"
}, 1000);

var k = {"abcde" : 22}


type PrimitiveArray = Array<string|number|boolean>;
type MyNumber = number;
//type NgScope = ng.IScope;
type Callback = () => void;


const enum Color { Blue, Green=3, Red };
var c = Color.Blue;
enum Colo4r {Red = 3, Green, Blue};
enum Colo43r // wefwfe
 {Red //rt
    =1, Green, Blue};

class AClass {

    constructor(argument) {
        // code...
    }
    public foo(bar: string|number ){ /* */
     }

    k = 22;

    public test() : string {
        var rectangle = { height: 20, width: 10 };
        var substitution = 0;
        let total = 0;

        this.foo("");

        var areaMessage = `Rectan$()[]{]}}"''#\/ \2123


        gle area is ${rectangle.height * rectangle.width}`;
        `literal${substitution}literal`
        var msg = `The total is ${total} (${total*1.05} with tax)`;

        `hello
there`;

        `${total}`;

        `${"hey"} ${"there"} what\777 \333 are ${"you"} doing`;
        `hey ${`there ${4} are`} you`;

        function func(a, ...we) {
            return a
        }

        func `a${total}c${"d"}`;
        func`a${total}c${"d"}`;

        "rr\74t \333z";

        func(33);

        let x = 5;
        for (let x = 1; x < 10; x++) {
            total += x;
        }
        console.log(x);
        return 'My name is ${firstname} ${lastname.toUpperCase()}'
    }
}

function f(x: number | number[]) {
  if (typeof x === "number") {
    return x + 10;
  }
  else {
    // return sum of numbers
  }
}
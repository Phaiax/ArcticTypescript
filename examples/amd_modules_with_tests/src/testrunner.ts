/// <reference path="lib/mocha/mocha.d.ts" />
/// <reference path="lib/chai/chai.d.ts" />
/// <reference path="lib/sinon-chai/sinon-chai.d.ts" />


import utilstest = require('./tests/utilstest');

mocha.setup('bdd');

utilstest.declare();

mocha.run();


/// <reference path="utils.ts" />

// every file will get compiled but
// there are no references, so
// $ nodejs program.js
// fill fail because utils.js is not included.

// Solution: use
//      tsconfig.json['compilerOptions']['out'] = 'out.js'
// to concat all output into one file,
// considering the sequence of imports automatically


console.log("Gravity" + Utils.g);

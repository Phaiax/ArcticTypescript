
// this is another source file
// there are no references to this file from other files mentioned in tsconfig.json[files]
// -> so this file has to be mentioned in tsconfig.json[files] to be compiled

// in contrast: insanity.ts is compiled automatically, because it is referenced in main.ts
// but it would be no harm, if insanity.ts would also be mentioned in tsconfig.json

// just make sure, you will use something like document.ready(function() {}) as
// an entry point for your code, if you have a larger codebase

(<any>window).main_two_has_been_executed = true;
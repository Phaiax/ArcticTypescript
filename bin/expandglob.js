
var expand = require('glob-expand');
var fs = require('fs');


// This file reads the tsconfig.json in the current working directory (cwd)
// and parses the "filesGlob" in the same way (with the same library) as
// atom-typescript does it. Writes the file to disk

// https://github.com/TypeStrong/atom-typescript/blob/master/lib/main/tsconfig/tsconfig.ts
// https://github.com/anodynos/node-glob-expand/blob/master/source/code/expand.coffee

// reads tsconfig in working dir
// expects filesGlob to exist

// returns {"error": "errormessage"} on failure
// returns {"error": false, files": []} on success



var projectFileName = 'tsconfig.json';
var dir = '.';
var projectFile = '';

try {
	if (!fs.existsSync(projectFileName)) {
		throw new Error("tsconfig.json does not exist in cwd");
	}
	try {
	    var projectFileTextContent = fs.readFileSync(projectFileName, 'utf8');
	}
	catch (ex) {
	    throw new Error("failed to read tsconfig.json");
	}
	try {
	    projectSpec = JSON.parse(projectFileTextContent);
	}
	catch (ex) {
	    throw new Error("json parsing of tsonfig.json failed");
	}
	if (!projectSpec.filesGlob) {
		throw new Error("tsonfig.json does not have field 'filesGlob'");
	}

	files = expand({ filter: 'isFile', cwd: dir }, projectSpec.filesGlob);
	projectSpec.files = files;

	var prettyJSONProjectSpec = prettyJSON(projectSpec);

	if (prettyJSONProjectSpec !== projectFileTextContent) {
	    fs.writeFileSync(projectFileName, prettyJSONProjectSpec);
	}

	console.log(JSON.stringify({"error": false, "files": files}));
}
catch (ex) {
	console.log(JSON.stringify({"error": ex.message}));
}



function prettyJSON(object) {
    var cache = [];
    var value = JSON.stringify(object, function (key, value) {
        if (typeof value === 'object' && value !== null) {
            if (cache.indexOf(value) !== -1) {
                return;
            }
            cache.push(value);
        }
        return value;
    }, 4);
    cache = null;
    return value;
}
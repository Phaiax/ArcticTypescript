module.exports = function(grunt) {
  // Do grunt-related things in here

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
	copy: {
	  main: {
	  	expand: true,
	  	cwd: 'res/',
	    src: ['**'],
	    dest: 'built/',
	  },
	},
  });


  grunt.loadNpmTasks('grunt-contrib-copy');

};
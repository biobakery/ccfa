module.exports = function(grunt) {
    
    grunt.initConfig({
	pkg: grunt.file.readJSON("package.json"),

	coffee: {
	    compile: {
		options: {
		    bare: true
		},
		files: {
		    "dist/assets/metadata.js": [ 
			"mibc/js/MIBC.coffee"
			, "mibc/js/metadata.js.coffee"
			]
		    , "dist/assets/validator.js": [ 
			"mibc/js/MIBC.coffee" 
			, "mibc/js/validator.js.coffee"
			]
		    , "dist/assets/samplemeta.js": [ 
			"mibc/js/MIBC.coffee" 
			, "mibc/js/samplemeta.js.coffee"
			]
		},
	    },
	},

	shell: {
	    bower: {
		options: {
		    stdout: true
		},
		command: "./node_modules/bower/bin/bower install"
	    },
	},

	copy: {
	    all: {
		files: [
		    {expand: true, cwd: "mibc/css/",
		     src: ["**"], dest: "dist/css/"},
		    {expand: true, cwd: "mibc/html/",
		     src: ["**"], dest: "dist/"},
		],
	    },
	},

	clean: {
	    all: {
		src: ['dist/*'],
	    },
	},

    });

    grunt.loadNpmTasks("grunt-contrib-coffee");
    grunt.loadNpmTasks("grunt-contrib-copy");
    grunt.loadNpmTasks("grunt-shell");

    grunt.registerTask("default", ["coffee", "shell", "copy"]);
    grunt.registerTask("dev", ["coffee", "copy"]);
    grunt.registerTask("clean", ["clean"]);

};
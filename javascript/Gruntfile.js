module.exports = function(grunt) {
    
    grunt.initConfig({
	pkg: grunt.file.readJSON("package.json"),

	coffee: {
	    compile: {
		options: {
		    bare: true
		},
		files: {
		    "mibc/dist/assets/mibc.js": "mibc/lib/test.coffee",
		    "mibc/dist/assets/metadata.js": "mibc/lib/metadata.js.coffee"
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
		     src: ["**"], dest: "mibc/dist/css/"},
		    {expand: true, cwd: "mibc/html/",
		     src: ["**"], dest: "mibc/dist/"},
		],
	    },
	},

	clean: {
	    all: {
		src: ['mibc/dist/*'],
	    },
	},

    });

    grunt.loadNpmTasks("grunt-contrib-coffee");
    grunt.loadNpmTasks("grunt-contrib-copy");
    grunt.loadNpmTasks("grunt-shell");

    grunt.registerTask("default", ["coffee", "shell", "copy"]);
    grunt.registerTask("clean", ["clean"]);

};
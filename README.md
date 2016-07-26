# bbee
Very simple C - C++ Builder

I wrote this little script to help me out with little C or C++ codes.

Sometimes I do not want to spend time writing Makefile scripts

thus while sending some sample codes to ppl, I include this.

This has a little convention so as long as you keep the convention, things will be successfully built.

Please note that, I did not wrote this little tiny script for big and complex projects, stick to cmake or autotools if you are planning to write sth complex.

Other than that, this script would do the job for you as well;

Here is a sample capul.json file

    {
        "name": "Hello World",
        "builder": "gcc",
        "sources": [
            "./src"
        ],
        "includes": [
            "./include"
        ],
        "libraries": [
            "pthread"
        ],
        "library_search_paths": [
            "/usr/local/lib"
        ],
        "output": "binary",
        "output_dir": "build",
        "output_name": "hello_world",
        "cflags": ""
    }

Note: just "sources", "output" fields are mandatory, others are optional.

**If you want to contribute, please keep the code a single file and pep8 should pass without errors or warnings**


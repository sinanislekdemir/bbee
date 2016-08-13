#!/usr/bin/env python

# Simple C builder
# This project is created for my own compiling requirements
# Coded by: sinan islekdemir
# TODO Pretty messy code, needs refactoring
# NOTE This code is meant to be a single file

import json
import os
import subprocess
import sys


# Stolen bcolors from stackowerflow #22886353
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


# I wrote this ehe :)
class CPrint:
    @staticmethod
    def header(msg):
        print bcolors.HEADER + msg + bcolors.ENDC

    @staticmethod
    def ok(msg):
        print bcolors.OKBLUE + msg + bcolors.ENDC

    @staticmethod
    def okg(msg):
        print bcolors.OKGREEN + msg + bcolors.ENDC

    @staticmethod
    def warning(msg):
        print bcolors.WARNING + msg + bcolors.ENDC

    @staticmethod
    def fail(msg):
        print bcolors.FAIL + msg + bcolors.ENDC


# Main builder class
class Builder(object):
    # TODO Constructor is damn too long, rewrite.
    def __init__(self, filename):
        if not os.path.isfile(filename):
            CPrint.fail("{} Not Found!".format(filename))
            exit(3)
        f = open(filename, 'r')
        data = f.read()
        f.close()
        obj = json.loads(data)
        self.builder = 'gcc'
        self.build_type = 'c'
        self.build = obj
        self.sources = []
        self.includes = []
        self.libraries = []
        self.library_search_paths = []
        self.output = ''
        self.output_dir = '.'
        self.output_name = 'output'
        self.cflags = ''
        self.debug = False
        self.source_extension = '.c'
        self.run_after_build = False
        if 'name' in obj:
            CPrint.header('Project name {}'.format(obj['name']))
        if 'builder' in obj:
            self.builder = obj['builder']
        if 'build_type' in obj:
            self.build_type = obj['build_type']
        if 'sources' in obj:
            self.sources = obj['sources']
        if 'includes' in obj:
            self.includes = obj['includes']
        if 'libraries' in obj:
            self.libraries = obj['libraries']
        if 'output' in obj:
            self.output = obj['output']
        if 'output_dir' in obj:
            self.output_dir = obj['output_dir']
        if 'output_name' in obj:
            self.output_name = obj['output_name']
        if 'cflags' in obj:
            self.cflags = obj['cflags']
        if 'debug' in obj:
            self.debug = obj['debug']
        if 'source_extension' in obj:
            self.source_extension = obj['source_extension']
        if 'run_after_build' in obj:
            self.run_after_build = obj['run_after_build']

    def clean(self):
        files = []
        CPrint.okg("Cleaning files ")
        for source in self.sources:
            if os.path.isdir(source):
                ls = os.listdir(source)
                for f in ls:
                    files.append(source + '/' + f)
                    if self.debug:
                        print "Find: [{}/{}]".format(source, f)
            if os.path.isfile(source):
                files.append(source)
                if self.debug:
                    print "Find [{}]".format(source)
        obj_files = []
        for file in files:
            if not file.endswith(self.source_extension):
                continue
            os.remove(file + '.o')
            if self.debug:
                print "Remove [{}]".format(file + '.o')

    def build_c(self):
        files = []
        CPrint.okg("Collecting files ")
        for source in self.sources:
            if os.path.isdir(source):
                ls = os.listdir(source)
                for f in ls:
                    if self.debug:
                        print "Add: {}/{}".format(source, f)
                    files.append(source + '/' + f)
            if os.path.isfile(source):
                files.append(source)
                if self.debug:
                    print "Add [{}]".format(source)
        obj_files = []
        for file in files:
            if not file.endswith(self.source_extension):
                continue
            command = ''
            command = self.builder
            command += ' -c "' + file + '"'
            command += ' -o "' + file + '.o"'
            command += ' ' + self.cflags
            obj_files.append(file + '.o')
            for inc in self.includes:
                command += ' -I"' + inc + '"'
            print "Building {} ".format(file)
            if self.debug:
                print "{}".format(command)
            call = subprocess.call(command, shell=True)
            if call > 0:
                CPrint.fail("Failed with {}".format(call))
                exit(127)
        if self.output == 'binary':
            command = self.builder
            command += ' -o "{}/{}" '.format(self.output_dir, self.output_name)
            command += " ".join(obj_files)
            command += ' ' + self.cflags
            for lib in self.library_search_paths:
                command += ' -L"' + lib + '"'
            for lib in self.libraries:
                command += ' -l' + lib
            if self.debug:
                print "{}".format(command)
            call = subprocess.call(command, shell=True)

            if call > 0:
                CPrint.fail('Failed with {}'.format(call))
                exit(127)
            if self.run_after_build:
                print "Running {}/{}".format(self.output_dir, self.output_name)
                os.system("{}/{}".format(self.output_dir, self.output_name))
        if self.output == 'library':
            command = 'ar -cvq "{}/{}" '.format(self.output_dir,
                                                self.output_name)
            command += ' '.join(obj_files)
            if self.debug:
                print "{}".format(command)
            call = subprocess.call(command, shell=True)
            if call > 0:
                CPrint.fail('Failed with {}'.format(call))
                exit(127)

    def run(self):
        CPrint.ok("Building using {}".format(self.builder))
        if self.build_type == 'c':
            self.build_c()


def help():
    import textwrap
    print textwrap.dedent("""\
        Build system by Sinan ISLEKDEMIR - sinan@islekdemir.com
        Parameters:
        -------------------------------------------------------
        --i=capul.json input capul file
        --output=directory set output directory
        --help show this help text
        --version shows version
        """)
    exit(0)

argsdict = {}

for farg in sys.argv:
    try:
        if farg.startswith('--'):
            (arg, val) = farg.split("=")
            arg = arg[2:]

            if arg in argsdict:
                argsdict[arg].append(val)
            else:
                argsdict[arg] = [val]
        else:
            argsdict[farg] = 1
    except:
        help()


if 'i' in argsdict:
    b = Builder(argsdict['i'][0])
else:
     # check of capul.json
    if not os.path.isfile('capul.json'):
        CPrint.fail("capul.json file not found ")
        exit(2)
    b = Builder('capul.json')

if 'help' in argsdict:
    help()

if 'clean' in argsdict:
    b.clean()
    exit(0)

b.run()

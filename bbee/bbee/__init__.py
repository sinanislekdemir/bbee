# Simple C builder
# This project is created for my own compiling requirements
# Coded by: sinan islekdemir
# NOTE This code is meant to be a single file

import collections
import json
import os
import platform
import stat
import subprocess
import sys
from shutil import copyfile


def convert(data):
    if isinstance(data, str):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

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


class CPrint:
    @staticmethod
    def header(msg):
        print(bcolors.HEADER + msg + bcolors.ENDC)

    @staticmethod
    def ok(msg):
        print(bcolors.OKBLUE + msg + bcolors.ENDC)

    @staticmethod
    def okg(msg):
        print(bcolors.OKGREEN + msg + bcolors.ENDC)

    @staticmethod
    def warning(msg):
        print(bcolors.WARNING + msg + bcolors.ENDC)

    @staticmethod
    def fail(msg):
        print(bcolors.FAIL + msg + bcolors.ENDC)


# Main builder class
class Builder(object):
    def __init__(self, filename):
        if not os.path.isfile(filename):
            CPrint.fail("{} Not Found!".format(filename))
            sys.exit(3)
        try:
            json_data = open(filename, 'r').read()
            obj = json.loads(json_data)
        except Exception as e:
            CPrint.fail("Unable to parse json file, {}".format(e))
            sys.exit(2)

        self.builder = obj.get('builder', 'gcc')
        self.build_type = obj.get('build_type', 'c')
        self.build = obj

        self.sources = obj.get('sources', [])
        self.includes = obj.get('includes', [])

        libraries = obj.get('libraries', [])
        linux_libraries = obj.get('linux_libraries', [])  # linux specific
        darwin_libraries = obj.get('darwin_libraries', [])  # apple specific
        windows_libraries = obj.get('windows_libraries', [])  # win specific

        self.library_search_paths = obj.get('library_search_paths', [])
        self.frameworks = obj.get('frameworks', [])  # apple specific

        self.output = obj.get('output', '')
        self.output_dir = obj.get('output_dir', '.')
        self.output_name = obj.get('output_name', 'output')
        self.cflags = obj.get('cflags', '')
        self.debug = obj.get('verbose', False)

        self.source_extension = obj.get('source_extension', '.c')
        self.run_after_build = obj.get('run_after_build', False)
        self.install = obj.get('install', [])

        self.ar_params = obj.get('ar', 'rcs')
        self.name = obj.get('name', '')
        self.libraries = {
            'common': libraries,
            'darwin': darwin_libraries,
            'linux': linux_libraries,
            'windows': windows_libraries
        }

    def clean(self):
        files = []
        CPrint.okg("Cleaning files ")
        for source in self.sources:
            if os.path.isdir(source):
                ls = os.listdir(source)
                for f in ls:
                    files.append(source + '/' + f)
                    if self.debug:
                        print("Find: [{}/{}]".format(source, f))
            if os.path.isfile(source):
                files.append(source)
                if self.debug:
                    print("Find [{}]".format(source))
        for file in files:
            if not file.endswith(self.source_extension):
                continue
            if os.path.isfile(file + '.o'):
                os.remove(file + '.o')
            if self.debug:
                print("Remove [{}]".format(file + '.o'))

    def build_c(self):
        files = []
        CPrint.okg("Collecting files ")
        for source in self.sources:
            if os.path.isdir(source):
                ls = os.listdir(source)
                for f in ls:
                    if self.debug:
                        print("Add: {}/{}".format(source, f))
                    files.append(source + '/' + f)
            if os.path.isfile(source):
                files.append(source)
                if self.debug:
                    print("Add [{}]".format(source))

        obj_files = []
        for file in files:
            if not file.endswith(self.source_extension):
                continue
            command = ''
            command = self.builder
            command += ' -c "' + file + '"'
            command += ' -o "' + file + '.o"'
            if type(self.cflags) is list:
                self.cflags = ' '.join(self.cflags)
            command += ' ' + self.cflags
            obj_files.append(file + '.o')
            for inc in self.includes:
                command += ' -I"' + inc + '"'
            print("Building {} ".format(file))
            if self.debug:
                print("{}".format(command))
            call = subprocess.call(command, shell=True)
            if call > 0:
                CPrint.fail("Failed with {}".format(call))
                sys.exit(127)

        if self.output == 'binary':
            command = self.builder
            command += ' -o "{}/{}" '.format(self.output_dir, self.output_name)
            command += " ".join(obj_files)
            command += ' ' + self.cflags
            for lib in self.library_search_paths:
                command += ' -L"' + lib + '"'
            for lib in self.libraries['common']:
                command += ' -l' + lib
            for lib in self.libraries[platform.system().lower()]:
                command += ' -l' + lib
            if platform.system().lower() == 'darwin':
                for framework in self.frameworks:
                    command += ' -framework ' + framework
            if self.debug:
                print("{}".format(command))
            call = subprocess.call(command, shell=True)

            if call > 0:
                CPrint.fail('Failed with {}'.format(call))
                sys.exit(127)
            if self.run_after_build:
                self.exec_bin()

        if self.output == 'library':
            command = 'ar {} "{}/{}" '.format(self.ar_params, self.output_dir,
                                              self.output_name)
            command += ' '.join(obj_files)
            if self.debug:
                print("{}".format(command))
            call = subprocess.call(command, shell=True)
            if call > 0:
                CPrint.fail('Failed with {}'.format(call))
                sys.exit(127)

    def exec_bin(self):
        print("Running {}/{}".format(self.output_dir, self.output_name))
        os.system("cd {} && ./{} && cd ..".format(self.output_dir,
                                                  self.output_name))

    def run(self):
        CPrint.ok("Building using {}".format(self.builder))
        if self.build_type == 'c':
            self.build_c()

    def do_install(self):
        if not self.install:
            CPrint.fail("No installation information found for project")
            return False
        self.install = convert(self.install)
        for definition in self.install:
            _from = definition[0]
            _to = definition[1]
            if not isinstance(_from, str):
                CPrint.fail("First parameter should be a single string")
                return False
            if not os.path.exists(_from):
                CPrint.fail("File or directory not found: [{}]".format(_from))
                return False
            if os.path.isdir(_from):
                _from = os.path.join(_from, ".")

            if isinstance(_to, str):
                if _to.startswith('!'):
                    _to = _to[1:]
                    os.system('mkdir -p "{}"'.format(_to))
                if os.path.isdir(_to):
                    print(_from)
                    os.system('cp -r "{}" "{}"'.format(_from, _to))
                else:
                    CPrint.fail("Target directory not found!")
                    return False

            if isinstance(_to, list):
                success = False
                for __to in _to:
                    if __to.startswith('!'):
                        __to = __to[1:]
                        os.system('mkdir -p "{}"'.format(__to))
                    if os.path.isdir(__to):
                        print(_from)
                        os.system('cp -r "{}" "{}"'.format(_from, __to))
                        success = True
                        break
                if not success:
                    CPrint.fail("All directories failed for installation")
        return True


def help():
    import textwrap
    print(textwrap.dedent("""\
        Build system by Sinan ISLEKDEMIR - sinan@islekdemir.com
        Parameters:
        -------------------------------------------------------
        --create create an empty C project here
        --create++ create an empty C++ project here
        --i=capul.json input capul file
        --output=directory set output directory
        --run only run output without building
        --help show this help text
        --version shows version
        --install installs the project to system wide
        --clean clean pre-built object files
        """))
    sys.exit(0)


def create_project(prefix=''):
    os.mkdir('sources')
    os.mkdir('includes')
    os.mkdir('build')
    # ok drop a copy of bbee to this directory
    copyfile(sys.argv[0], 'bbee')
    st = os.stat('bbee')
    os.chmod('bbee', st.st_mode | stat.S_IEXEC)
    with open('README.md', 'w') as f:
        f.write("# bbee project\n")
    include = "<stdio.h>"
    if prefix == "++":
        include = "<iostream>"
    code = 'printf("hello from bbee!\\n");'
    if prefix == "++":
        code = 'std::cout << "hello from bbee!\\n";'
    main = """
#include %s
int main()
{
    %s
}
    """ % (include, code)
    f = open("sources/main.c%s" % prefix, 'w')
    f.write(main)
    f.close()
    cc = "cc"
    if prefix == "++":
        cc = "++"
    with open('capul.json', 'w') as f:
        data = {'name': 'Example Project',
                'builder': 'g%s' % cc,
                'sources': ['./sources'],
                'includes': ['./includes'],
                'libraries': [],
                'linux_libraries': [],
                'darwin_libraries': [],
                'windows_libraries': [],
                'library_search_paths': [],
                'output': 'binary',
                'output_dir': 'build',
                'output_name': 'example',
                'cflags': '',
                'ar': 'rcs',
                'verbose': True,
                'install': [],
                'frameworks': [],
                'source_extension': '.c%s' % prefix,
                'run_after_build': True}
        f.write(json.dumps(data, indent=4, sort_keys=True))


def main():
    argsdict = {}

    for farg in sys.argv:
        try:
            if farg.startswith('--'):
                if '=' in farg:
                    (arg, val) = farg.split("=")
                    arg = arg[2:]
                else:
                    arg = farg[2:]
                    val = ''
                if arg in argsdict:
                    argsdict[arg].append(val)
                else:
                    argsdict[arg] = [val]
            else:
                argsdict[farg] = 1
        except Exception as e:
            print(e)
            help()

    if 'create' in argsdict:
        create_project()
        exit(0)

    if 'create++' in argsdict:
        create_project('++')
        exit(0)

    if 'i' in argsdict:
        b = Builder(argsdict['i'][0])
    else:
        # check of capul.json
        if not os.path.isfile('capul.json'):
            CPrint.fail("capul.json file not found ")
            help()
            exit(2)
        b = Builder('capul.json')

    if 'help' in argsdict:
        help()

    if 'clean' in argsdict:
        b.clean()
        exit(0)

    if 'install' in argsdict:
        res = b.do_install()
        exit(res)

    if 'run' in argsdict:
        b.exec_bin()
        exit(0)

    b.run()


if __name__ == '__main__':
    main()

import subprocess

from django.conf import settings

from compress.filter_base import FilterBase, FilterError

BINARY = getattr(settings, 'COMPRESS_CLOSURE_BINARY', 'java -jar compiler.jar')
JS_ARGUMENTS = getattr(settings, 'COMPRESS_CLOSURE_JS_ARGUMENTS', '')

class GoogleClosureCompilerFilter(FilterBase):

    def filter_common(self, content, arguments):
        command = BINARY
        for argument in arguments:
            command += ' --' + argument + ' ' + arguments[argument]

        if self.verbose:
            command += ' --verbose'

        p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE)
        p.stdin.write(content)

        filtered_css, err = p.communicate()

        if p.wait() != 0:
            if not err:
                err = 'Unable to apply Google Closure Compiler filter'

            raise FilterError(err)

        if self.verbose:
            print err

        return filtered_css

    def filter_js(self, js):
        return self.filter_common(js, JS_ARGUMENTS)
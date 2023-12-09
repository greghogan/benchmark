import multiprocessing
import os.path
import psutil


class CruncherConfig:
    constants = {}
    constants['pi'] = '''Constant : "pi"
            Algorithm : "chudnovsky"'''

    constants['e_α'] = '''Constant : "e"
            Algorithm : "exp(1)"'''
    constants['e_β'] = '''Constant : "e"
            Algorithm : "exp(-1)"'''

    constants['euler_mascheroni_α'] = '''Constant : "gamma"
            Algorithm : "brent-refined"'''
    constants['euler_mascheroni_β'] = '''Constant : "gamma"
            Algorithm : "brent-original"'''

    constants['sqrt2'] = '''Constant : "sqrt"
            Argument : 2
            Algorithm : "newton"'''
    constants['sqrt200'] = '''Constant : "sqrt"
            Argument : 200
            Algorithm : "newton"'''

    constants['golden_ratio'] = '''Constant : "goldenratio"
            Algorithm : "newton"'''
    constants['sqrt125'] = '''Constant : "sqrt"
            Argument : 125
            Algorithm : "newton"'''

    constants['log2_α'] = '''Constant : "log"
            Argument : 2
            Algorithm : "machin-primary"'''
    constants['log2_β'] = '''Constant : "log"
            Argument : 2
            Algorithm : "machin-secondary"'''

    constants['zeta3_α'] = '''Constant : "zeta3"
            Algorithm : "zuniga2023vi"'''
    constants['zeta3_β'] = '''Constant : "zeta3"
            Algorithm : "zuniga2023v"'''

    constants['catalans_α'] = '''Constant : "catalan"
            Algorithm : "pilehrood-short"'''
    constants['catalans_β'] = '''Constant : "catalan"
            Algorithm : "zuniga2023"'''

    constants['lemniscate_α'] = '''Constant : "lemniscate"
            Algorithm : "zuniga2023x"'''
    constants['lemniscate_β'] = '''Constant : "lemniscate"
            Algorithm : "guillera"'''

    constants['log10_α'] = '''Constant : "log"
            Argument : 10
            Algorithm : "machin-primary"'''
    constants['log10_β'] = '''Constant : "log"
            Argument : 10
            Algorithm : "machin-secondary"'''

    # ancilliary constants

    constants['sqrt325'] = '''Constant : "sqrt"
            Argument : 325
            Algorithm : "newton"'''

    constants['log3_α'] = '''Constant : "log"
            Argument : 3
            Algorithm : "machin-primary"'''
    constants['log3_β'] = '''Constant : "log"
            Argument : 3
            Algorithm : "machin-secondary"'''

    constants['log5_α'] = '''Constant : "log"
            Argument : 5
            Algorithm : "machin-primary"'''
    constants['log5_β'] = '''Constant : "log"
            Argument : 5
            Algorithm : "machin-secondary"'''

    constants['log7_α'] = '''Constant : "log"
            Argument : 7
            Algorithm : "machin-primary"'''
    constants['log7_β'] = '''Constant : "log"
            Argument : 7
            Algorithm : "machin-secondary"'''

    def __init__(self, constant, output_enable, template, root_dir):
        self.threads = multiprocessing.cpu_count()
        print('Running with {} threads'.format(self.threads))

        if constant in CruncherConfig.constants:
            self.constant = CruncherConfig.constants[constant]
        else:
            with open(os.path.join('Custom Formulas', constant + '.cfg'), 'r', newline='\r\n') as file:
                data = file.read()
                # ignore up to the first comment slash which ignores the UTF-16 BOM
                data = data[data.find('/'):]

                # skip the opening and closing curly braces (comments will be stripped from the output config dump)
                data = '\n'.join(line for line in data.split('\n') if not line or line[0] not in '{}')

                self.constant = 'Constant : "custom"\n' + data

        if output_enable:
            self.output = '''Framework : "ycd"
            Path : ""
            DigitsPerFile : 0
            RawIO : "true"'''
        else:
            self.output = '''Framework : "none"
            Path : ""'''

        config_template_filename = os.path.join(root_dir, 'templates', template)
        with open(config_template_filename, 'r', newline='\r\n') as file:
            self.config_template = file.read()

            # escape for 'format'ing below
            self.config_template = self.config_template.replace('{', '{{')
            self.config_template = self.config_template.replace('}', '}}')
            self.config_template = self.config_template.replace('<', '{')
            self.config_template = self.config_template.replace('>', '}')

    def write(self, digits):
        with open('run.cfg', 'w') as file:
            keys = {"constant": self.constant, "digits": digits, "threads": self.threads,
                    "output": self.output, "memory": int(0.95 * psutil.virtual_memory().available)}
            file.write(self.config_template.format(**keys))

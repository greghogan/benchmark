import re


class ParseCruncherValidation:
    re_platform_instance = re.compile(r'User:\s+(.*)\s+\((.*)\)')
    re_constant = re.compile(r'Constant:\s+(?:Custom - )?(.*)')
    re_algorithm = re.compile(r'Algorithm : "(.*)"')
    re_name_short = re.compile(r'NameShort : "(.*)"')
    re_name_long = re.compile(r'NameLong : "(.*)"')
    re_algorithm_short = re.compile(r'AlgorithmShort : "(.*)"')
    re_digits = re.compile(r'Decimal Digits:\s+([\d,]+)')
    re_time = re.compile(r'Total Computation Time:\s+(\d+)\.(\d+) seconds')

    def __init__(self, filename):
        with open(filename, 'r') as file:
            output = file.read()

            platform_instance = ParseCruncherValidation.re_platform_instance.search(output)
            self.platform = platform_instance[1]
            self.instance = platform_instance[2]

            name_short = ParseCruncherValidation.re_name_short.search(output)
            self.constant = name_short[1] if name_short else ParseCruncherValidation.re_constant.search(output)[1]

            algorithm_short = ParseCruncherValidation.re_algorithm_short.search(output)
            self.algorithm = algorithm_short[1] if algorithm_short else ParseCruncherValidation.re_algorithm.search(output)[1]

            self.digits = int(ParseCruncherValidation.re_digits.search(output)[1].replace(',', ''))

            time = ParseCruncherValidation.re_time.search(output)
            self.milliseconds = 1000 * int(time[1]) + int(time[2])

import os.path
import re


class ParseCruncherOutput:
    re_time = re.compile(r'Total Computation Time:\s+\x1b\[01;33m(\d+)\.(\d+) seconds')
    re_file = re.compile(r'Validation File: \x1b\[01;35m(.* - \d{8}-\d{6}.txt)')

    def __init__(self, output):
        self.output = output

        time = ParseCruncherOutput.re_time.search(output)
        self.milliseconds = 1000 * int(time[1]) + int(time[2])

        self.validation_filename = ParseCruncherOutput.re_file.search(output)[1]

    def write(self, results_path):
        # write output captured from stdout to file
        output_filename = self.validation_filename[:-4] + '.out'
        with open(os.path.join(results_path, output_filename), 'w') as file:
            file.write(self.output)

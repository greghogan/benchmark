#!/usr/bin/env python3

import argparse
import datetime
import os.path
import shutil
import subprocess
import sys
import time

from lib.CruncherConfig import CruncherConfig
from lib.DigitsCount import DigitsCount
from lib.ParseCruncherOutput import ParseCruncherOutput
from lib.SystemInfo import SystemInfo

parser = argparse.ArgumentParser(description='Benchmark y-cruncher with multi-variate configurations')
parser.add_argument('--constant', required=True,
                    help='name of constant to compute')
parser.add_argument('--output_enable', action='store_true',
                    help='whether to store digits')
parser.add_argument('--results', required=True,
                    help='directory in which to store results')
parser.add_argument('--template', required=True,
                    help='path to configuration template file')
parser.add_argument('digits', metavar='D', nargs='+',
                    help='mapping from number of digits to optional count ("25m:10 50m:5 100m")')
args = parser.parse_args()


if not os.path.exists(args.results):
    os.makedirs(args.results)


script_dir = os.path.dirname(sys.argv[0])
root_dir = os.path.dirname(script_dir)


info = SystemInfo()
info.write_username_txt(os.path.join(root_dir, 'templates', 'username.template'))

config = CruncherConfig(args.constant, args.output_enable, args.template, root_dir)

print()

# prevent overwriting previous execution
time.sleep(0.5)

# http://tylernakamura.com/2018/07/10/numa-information-without-numactl/
numactl = subprocess.run(['which', 'numactl'], capture_output=True).stdout.decode('utf-8').rstrip('\n')

for digits_count in args.digits:
    digits = DigitsCount(digits_count)
    config.write(digits.digits)

    print('{} [0/{}] {}, digits: {}'.format(
        datetime.datetime.now(), digits.count, args.constant, digits.digits_string))
    total_ms = 0
    min_ms = None

    for i in range(digits.count):
        # if args.output_enable:
        #     cmd = ['sudo', './y-cruncher', 'config', 'run.cfg']
        #     lines = []
        #
        #     popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        #     for line in popen.stdout:
        #         #line_decoded = line.decode('utf-8')
        #         print(line, end='')
        #         lines.append(line)
        #     popen.stdout.close()
        #     return_code = popen.wait()
        #     if return_code:
        #         raise subprocess.CalledProcessError(return_code, cmd)
        #     output = ParseCruncherOutput(''.join(lines))
        #else:
        if info.on_wsl:
            # https://stackoverflow.com/questions/47038990/python-subprocess-cannot-capture-output-of-windows-program

            # import win32console
            # import subprocess
            # import msvcrt
            # import os
            #
            # ccsb = win32console.CreateConsoleScreenBuffer()
            # fd = msvcrt.open_osfhandle(ccsb, os.O_APPEND)
            # proc = subprocess.Popen(['C:\\Users\\me\\program.exe'], stdout=fd)
            # proc.wait()
            # ccsb.ReadConsoleOutputCharacter(100, win32console.PyCOORDType(0,0)) # reads 100 characters from the first line
            result = subprocess.run(['./y-cruncher.exe', 'config', 'run.cfg'], capture_output=True)
        else:
            #result = subprocess.run(['sudo', numactl, '--interleave=all', './y-cruncher', 'config', 'run.cfg'], capture_output=True)
            result = subprocess.run(['sudo', './y-cruncher', 'config', 'run.cfg'], capture_output=True)
        output = ParseCruncherOutput(result.stdout.decode('utf-8'))
        output.write(args.results)

        # move validation file to results directory
        shutil.move(output.validation_filename, os.path.join(args.results, output.validation_filename))

        # move configuration file to results directory
        config_filename = output.validation_filename[:-4] + '.cfg'
        shutil.copy2('run.cfg', os.path.join(args.results, config_filename))

        total_ms += output.milliseconds
        if not min_ms or output.milliseconds < min_ms:
            min_ms = output.milliseconds

        print('{} [{}/{}] {}, ms: {}, avg ms: {}, min ms: {}'.format(
            datetime.datetime.now(), i + 1, digits.count, args.constant, output.milliseconds, total_ms // (i + 1), min_ms))

        # sleep up to 1/2 second to prevent filename collision
        time.sleep(max(0, 500 - output.milliseconds) / 1000)

        # stop early if over time limit
        if digits.limit_ms and total_ms > digits.limit_ms:
            break

    print()

#!/usr/bin/env python3

import collections
import math
import os.path
import pathlib
import sys

from lib.ParseCruncherValidation import ParseCruncherValidation


# see "What Constants are Tracked" at http://www.numberworld.org/y-cruncher/records.html
priorities = {
    "Pi": 1,
    "e": 2,
    "Euler-Mascheroni Constant": 3,
    "Sqrt(2)": 4,
    "Sqrt(200)": 4,
    "Golden Ratio": 5,
    "Sqrt(125)": 5,
    "Log(2)": 6,
    "Zeta(3) - Apery's Constant": 7,
    "Catalan's Constant": 8,
    "Lemniscate": 9,
    "Lemniscate Constant": 9,
    "Gamma(¼)": 10,
    "Gamma(⅓)": 11,
    "Log(10)": 12,
    "Zeta(5)": 13
}

def removesuffix(self, suffix):
    # suffix='' should not call self[:-0].
    if suffix and self.endswith(suffix):
        return self[:-len(suffix)]
    else:
        return self[:]


def round_to_significant_figures(number, figures):
    exp = math.ceil(math.log10(number)) - figures
    pwr = 10**exp
    return int(pwr * int(number / pwr))


suffixes = {12: 't', 9: 'b', 6: 'm', 3: 'k'}

def digit_string(digits):
    power = 0
    suffix = ''

    for power, suffix in suffixes.items():
        if digits >= 10**power:
            break

    return removesuffix(str(digits / 10**power), '.0') + suffix


base_dir = pathlib.Path(os.path.dirname(sys.path[0]))
fetch_dir = base_dir / 'fetch'
results_dir = base_dir / 'results'

# sort fetched results into directory by platform / instance / constant
for filename in fetch_dir.glob('*.txt'):
    validation = ParseCruncherValidation(filename)

    dir = results_dir / validation.platform / validation.instance /'{} [{}]'.format(validation.constant.replace('/', '∕'), validation.algorithm)
    if not dir.exists():
        os.makedirs(dir)

    filebase, _ = os.path.splitext(os.path.basename(filename))
    for ext in ['.cfg', '.out', '.txt']:
        (fetch_dir / (filebase + ext)).rename(dir / (filebase + ext))

for platform in os.listdir(results_dir):
    platform_dir = results_dir / platform
    if not platform_dir.is_dir():
        continue

    for instance in os.listdir(platform_dir):
        instance_dir = platform_dir / instance
        if not instance_dir.is_dir():
            continue

        digits = set()
        executions = set()
        milliseconds = {}
        basepaths = {}

        for constant in os.listdir(instance_dir):
            constant_dir = instance_dir / constant
            if not constant_dir.is_dir():
                continue

            basename_groups = collections.defaultdict(set)
            for filename in os.listdir(constant_dir):
                basename, extension = os.path.splitext(filename)
                basename_groups[basename].add(extension)

                basepath = os.path.join(constant_dir, basename)
                filepath = os.path.join(constant_dir, filename)
                if not os.path.isfile(filepath) or not extension == '.txt':
                    continue

                validation = ParseCruncherValidation(filepath)
                execution = (validation.constant, validation.algorithm)

                if execution not in executions:
                    executions.add(execution)

                if validation.digits not in digits:
                    digits.add(validation.digits)

                if (validation.digits, execution) in milliseconds:
                    old_basepath = basepaths[validation.digits, execution]

                    # only replace if faster
                    if validation.milliseconds < milliseconds[validation.digits, execution] or \
                            (validation.milliseconds == milliseconds[validation.digits, execution] and basepath < old_basepath):
                        print("removing " + old_basepath)
                        os.remove(old_basepath + '.txt')
                        os.remove(old_basepath + '.cfg')
                        os.remove(old_basepath + '.out')

                        milliseconds[validation.digits, execution] = validation.milliseconds
                        basepaths[validation.digits, execution] = basepath
                    else:
                        print("removing " + basepath)
                        os.remove(basepath + '.txt')
                        os.remove(basepath + '.cfg')
                        os.remove(basepath + '.out')
                else:
                    milliseconds[validation.digits, execution] = validation.milliseconds
                    basepaths[validation.digits, execution] = basepath

            for basename, group in basename_groups.items():
                if group != {'.cfg', '.out', '.txt'}:
                    print("missing files for '{}'".format(basename))

        digits = sorted(digits)

        with open(os.path.join(results_dir, '{} [{}].csv'.format(platform, instance)), 'w') as file:
            file.write(',')
            for digit in digits:
                file.write(',')
                file.write(digit_string(digit))
                file.write(',')
            file.write('\n')

            for execution in sorted(executions):
                constant, algorithm = execution

                file.write('"{} [{}]",'.format(constant, algorithm))
                if constant in priorities:
                    file.write(str(priorities[constant]))

                for digit in digits:
                    file.write(',')
                    if (digit, execution) in milliseconds:
                        file.write('{:.3f}'.format(milliseconds[digit, execution] / 1000))
                        file.write(',')
                        rate = digit * 1000 / milliseconds[digit, execution]
                        file.write('"{:,}"'.format(round_to_significant_figures(rate, 3)))
                    else:
                        file.write(',')
                file.write('\n')

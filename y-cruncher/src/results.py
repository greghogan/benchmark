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

results_by_instance_dir = results_dir / 'Tables by instance'
os.makedirs(results_by_instance_dir, exist_ok=True)
results_by_constant_dir = results_dir / 'Tables by constant'
os.makedirs(results_by_constant_dir, exist_ok=True)

# sort fetched results into directory by platform / instance / constant
for filename in fetch_dir.glob('*.txt'):
    validation = ParseCruncherValidation(filename)

    dir = results_dir / validation.platform / validation.instance /'{} [{}]'.format(validation.constant.replace('/', '∕'), validation.algorithm)
    os.makedirs(dir, exist_ok=True)

    filebase, _ = os.path.splitext(os.path.basename(filename))
    for ext in ['.cfg', '.out', '.txt']:
        (fetch_dir / (filebase + ext)).rename(dir / (filebase + ext))

# instance => digits
digits_by_instance = collections.defaultdict(set)
# constant => digits
digits_by_execution = collections.defaultdict(set)

# instance => execution => digit => milliseconds
executions_by_instance = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
# execution => instance => digit => milliseconds
instances_by_execution = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))

for platform in os.listdir(results_dir):
    platform_dir = results_dir / platform
    if not platform_dir.is_dir():
        continue

    for machine_type in os.listdir(platform_dir):
        machine_type_dir = platform_dir / machine_type
        if not machine_type_dir.is_dir():
            continue

        instance = (platform, machine_type)

        basepaths = {}

        for constant in os.listdir(machine_type_dir):
            constant_dir = machine_type_dir / constant
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

                digits_by_instance[instance].add(validation.digits)
                # don't display low-digits results in the execution tables
                if validation.digits >= 25_000_000:
                    digits_by_execution[execution].add(validation.digits)

                if validation.digits in executions_by_instance[instance][execution]:
                    milliseconds = executions_by_instance[instance][execution][validation.digits]
                    old_basepath = basepaths[validation.digits]

                    # only replace if faster
                    if validation.milliseconds < milliseconds or \
                            (validation.milliseconds == milliseconds and basepath < old_basepath):
                        print("removing " + old_basepath)
                        os.remove(old_basepath + '.txt')
                        os.remove(old_basepath + '.cfg')
                        os.remove(old_basepath + '.out')

                        executions_by_instance[instance][execution][validation.digits] = validation.milliseconds
                        instances_by_execution[execution][instance][validation.digits] = validation.milliseconds
                        basepaths[validation.digits] = basepath
                    else:
                        print("removing " + basepath)
                        os.remove(basepath + '.txt')
                        os.remove(basepath + '.cfg')
                        os.remove(basepath + '.out')
                else:
                    executions_by_instance[instance][execution][validation.digits] = validation.milliseconds
                    instances_by_execution[execution][instance][validation.digits] = validation.milliseconds
                    basepaths[validation.digits] = basepath

            for basename, group in basename_groups.items():
                if group != {'.cfg', '.out', '.txt'}:
                    print("missing files for '{}'".format(basename))

# file per instance
# table execution x digits
# cells milliseconds and digits/sec
for instance, executions in executions_by_instance.items():
    platform, machine_type = instance
    digits = digits_by_instance[instance]

    with open(os.path.join(results_by_instance_dir, '{} [{}].csv'.format(platform, machine_type)), 'w') as file:
        file.write(',')
        for digit in sorted(digits):
            file.write(',')
            file.write(digit_string(digit))
            file.write(',')
        file.write('\n')

        for execution in sorted(executions):
            constant, algorithm = execution
            milliseconds = executions[execution]

            file.write('"{} [{}]",'.format(constant, algorithm))
            if constant in priorities:
                file.write(str(priorities[constant]))

            for digit in sorted(digits):
                file.write(',')
                if digit in milliseconds:
                    file.write('{:.3f}'.format(milliseconds[digit] / 1000))
                    file.write(',')
                    rate = digit * 1000 / milliseconds[digit]
                    file.write('"{:,}"'.format(round_to_significant_figures(rate, 3)))
                else:
                    file.write(',')
            file.write('\n')

# file per constant
# table instance x digits
# cells milliseconds and digits/sec
for execution, instances in instances_by_execution.items():
    constant, algorithm = execution
    digits = digits_by_execution[execution]

    with open(os.path.join(results_by_constant_dir, '{} [{}].csv'.format(constant, algorithm)), 'w') as file:
        for digit in sorted(digits):
            file.write(',')
            file.write(digit_string(digit))
            file.write(',')
        file.write('\n')

        for instance in sorted(instances):
            platform, machine_type = instance
            milliseconds = instances[instance]

            file.write('"{} [{}]",'.format(platform, machine_type))

            for idx, digit in enumerate(sorted(digits)):
                if idx > 0:
                    file.write(',')
                if digit in milliseconds:
                    file.write('{:.3f}'.format(milliseconds[digit] / 1000))
                    file.write(',')
                    rate = digit * 1000 / milliseconds[digit]
                    file.write('"{:,}"'.format(round_to_significant_figures(rate, 3)))
                else:
                    file.write(',')
            file.write('\n')
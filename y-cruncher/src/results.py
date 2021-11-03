#!/usr/bin/env python3

import collections
import datetime
import math
import os
import pathlib
import re
import sys
import urllib.parse

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


re_filename_date_time = re.compile(r'.* - (\d{8})-(\d{6})')

base_dir = pathlib.Path(sys.path[0]).parent
fetch_dir = base_dir / 'fetch'
results_dir = base_dir / 'results'

results_by_instance_dir = results_dir / 'Tables by instance'
os.makedirs(results_by_instance_dir, exist_ok=True)
results_by_constant_dir = results_dir / 'Tables by constant'
os.makedirs(results_by_constant_dir, exist_ok=True)
best_times_by_constant_dir = results_dir / 'Best times by constant'
os.makedirs(best_times_by_constant_dir, exist_ok=True)

# sort fetched results into directory by platform / instance / constant
for filename in fetch_dir.glob('*.txt'):
    validation = ParseCruncherValidation(filename)

    dir = results_dir / validation.platform / validation.instance /'{} [{}]'.format(validation.constant.replace('/', '∕'), validation.algorithm)
    os.makedirs(dir, exist_ok=True)

    for ext in ['.cfg', '.out', '.txt']:
        src = filename.with_suffix(ext)
        dst = (dir / filename.stem).with_suffix(ext)
        src.rename(dst)

# instance => digits
digits_by_instance = collections.defaultdict(set)
# constant => digits
digits_by_execution = collections.defaultdict(set)

# instance => execution => digit => data dictionary
executions_by_instance = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
# execution => instance => digit => data dictionary
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

        for constant in os.listdir(machine_type_dir):
            constant_dir = machine_type_dir / constant
            if not constant_dir.is_dir():
                continue

            basename_groups = collections.defaultdict(set)
            for filename in pathlib.Path.iterdir(constant_dir):
                basename_groups[filename.with_suffix('')].add(filename.suffix)

                if not filename.is_file() or filename.suffix != '.txt':
                    continue

                validation = ParseCruncherValidation(filename)
                execution = (validation.constant, validation.algorithm)

                digits_by_instance[instance].add(validation.digits)
                # don't display low-digits results in the execution tables
                if validation.digits >= 25_000_000:
                    digits_by_execution[execution].add(validation.digits)

                date = datetime.datetime.strptime(re_filename_date_time.search(filename.stem)[1], "%Y%m%d")
                data = {'filename': filename, 'platform': validation.platform, 'instance': validation.instance,
                        'date': date, 'milliseconds': validation.milliseconds}

                if validation.digits in executions_by_instance[instance][execution]:
                    old_data = executions_by_instance[instance][execution][validation.digits]
                    milliseconds = old_data['milliseconds']
                    current_filename = old_data['filename']

                    # only replace if faster
                    if validation.milliseconds < milliseconds or \
                            (validation.milliseconds == milliseconds and filename < current_filename):
                        print(f'removing {current_filename}')
                        current_filename.unlink()
                        current_filename.with_suffix('.cfg').unlink()
                        current_filename.with_suffix('.out').unlink()

                        executions_by_instance[instance][execution][validation.digits] = data
                        instances_by_execution[execution][instance][validation.digits] = data
                    else:
                        print(f'removing {filename}')
                        filename.unlink()
                        filename.with_suffix('.cfg').unlink()
                        filename.with_suffix('.out').unlink()
                else:
                    executions_by_instance[instance][execution][validation.digits] = data
                    instances_by_execution[execution][instance][validation.digits] = data

            for basename, group in basename_groups.items():
                if group != {'.cfg', '.out', '.txt'}:
                    print(f"missing files for '{basename} with {group}'")

# file per instance
# table execution x digits
# cells milliseconds and digits/sec
for instance, executions in executions_by_instance.items():
    platform, machine_type = instance
    digits = digits_by_instance[instance]

    with open(results_by_instance_dir / '{} [{}].csv'.format(platform, machine_type), 'w') as file:
        file.write(',')
        for digit in sorted(digits):
            file.write(',')
            file.write(digit_string(digit))
            file.write(',')
        file.write('\n')

        for execution in sorted(executions):
            constant, algorithm = execution
            times = executions[execution]

            file.write('"{} [{}]",'.format(constant, algorithm))
            if constant in priorities:
                file.write(str(priorities[constant]))

            for digit in sorted(digits):
                file.write(',')
                if digit in times:
                    data = times[digit]
                    milliseconds = data['milliseconds']

                    file.write('{:.3f}'.format(milliseconds / 1000))
                    file.write(',')
                    rate = digit * 1000 / milliseconds
                    file.write('"{:,}"'.format(round_to_significant_figures(rate, 3)))
                else:
                    file.write(',')
            file.write('\n')

# file per constant
# table instance x digits
# cells milliseconds and digits/sec
for execution, instances in instances_by_execution.items():
    constant, algorithm = execution
    digits = sorted(digits_by_execution[execution])

    # digit => milliseconds
    best_times = {}

    with open(results_by_constant_dir / '{} [{}].csv'.format(constant, algorithm), 'w') as file:
        for digit in digits:
            file.write(',')
            file.write(digit_string(digit))
            file.write(',')
        file.write('\n')

        for instance in sorted(instances):
            platform, machine_type = instance
            times = instances[instance]

            file.write('"{} [{}]",'.format(platform, machine_type))

            for idx, digit in enumerate(digits):
                if idx > 0:
                    file.write(',')
                if digit in times:
                    data = times[digit]
                    milliseconds = data['milliseconds']

                    file.write('{:.3f}'.format(milliseconds / 1000))
                    file.write(',')
                    rate = round_to_significant_figures(digit * 1000 / milliseconds, 3)
                    file.write('"{:,}"'.format(rate))

                    if digit not in best_times or milliseconds < best_times[digit]['milliseconds']:
                        best_times[digit] = data
                else:
                    file.write(',')

            file.write('\n')

    # create markdown files with links to the fastest execution for each computation size
    with open(best_times_by_constant_dir / f'{constant} [{algorithm}].md', 'w') as file:
        file.write('| Digits | Seconds | Digits / Second | Platform | Instance | Date | Files |\n')
        file.write('| ------ | ------- | --------------- | -------- | -------- | ---- | ----- |\n')

        for digit in sorted(best_times):
            data = best_times[digit]
            filename = data['filename']
            platform = data['platform']
            instance = data['instance']
            date = data['date']
            milliseconds = data['milliseconds']
            rate = round_to_significant_figures(digit * 1000 / milliseconds, 3)

            link = pathlib.Path('..') / filename.relative_to(results_dir).with_suffix('')
            quoted = urllib.parse.quote(str(link))

            file.write(f'| {digit_string(digit)} | {milliseconds/1000:.3f} | {rate:,} | {platform} | {instance} | {date:%Y-%m-%d} | ')
            for suffix in ['cfg', 'out', 'txt']:
                file.write(f'[{suffix}]({quoted}.{suffix}) ')
            file.write(f'|\n')

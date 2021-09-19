import decimal
import sys


class DigitsCount:
    decimal.getcontext().traps[decimal.Inexact] = True

    def __init__(self, digits_count):
        limit_ms = 0

        colons = digits_count.count(':')
        if colons > 2:
            print('Malformed configuration! "{}" should be "<digits>[:<count>[:<seconds>]]'.format(digits_count))
            sys.exit(1)
        elif colons == 2:
            digit_string, count, limit_ms = digits_count.split(':')
        elif colons == 1:
            digit_string, count = digits_count.split(':')
        else:
            digit_string = digits_count
            count = 1

        if digit_string.lower().endswith('k'):
            digits = (decimal.Decimal(digit_string[:-1]) * 1_000).to_integral_exact()
        elif digit_string.lower().endswith('m'):
            digits = (decimal.Decimal(digit_string[:-1]) * 1_000_000).to_integral_exact()
        elif digit_string.lower().endswith('b'):
            digits = (decimal.Decimal(digit_string[:-1]) * 1_000_000_000).to_integral_exact()
        elif digit_string.lower().endswith('t'):
            digits = (decimal.Decimal(digit_string[:-1]) * 1_000_000_000_000).to_integral_exact()
        else:
            digits = decimal.Decimal(digit_string).to_integral_exact()

        self.digits_string = digit_string
        self.digits = digits
        self.count = int(count)
        self.limit_ms = 1000 * int(limit_ms)

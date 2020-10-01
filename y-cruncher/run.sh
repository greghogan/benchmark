#!/bin/sh

#   #         Constant                      Value        Approximate Difficulty*
# Fast Constants:
#   0         Sqrt(n)                                         1.46
#   1         Golden Ratio                = 1.618034...       1.46
#   2         e                           = 2.718281...       3.88 / 3.88
# Moderate Constants:
#   3         Pi                          = 3.141592...       13.2 / 19.9
#   4         Log(n)                                        > 35.7
#   5         Zeta(3) (Apery's Constant)  = 1.202056...       62.8 / 65.7
#   6         Catalan's Constant          = 0.915965...       78.0 / 105.
#   7         Lemniscate                  = 5.244115...       60.4 / 124. / 154.
# Slow Constants:
#   8         Euler-Mascheroni Constant   = 0.577215...       383. / 574.

# http://www.numberworld.org/y-cruncher/records.html
# 1: pi
# 2: e
# 3: euler_mascheroni
# 4: sqrt2
# 5: golden_ratio
# 6: log2
# 7: zeta3
# 8: catalans
# 9: lemniscate
# 10: 'Gamma(1d4) - AGM-Pi' or 'Gamma(1d4) - Series-Pi'
# 11: 'Gamma(1d3) - AGM-Pi' or 'Gamma(1d3) - Series-Pi'
# 12: log10
# 13: 'Zeta(5) - BBP-Kruse' or 'Zeta(5) - Broadhurst (optimized)'

# https://linuxreviews.org/HOWTO_make_Linux_run_blazing_fast_(again)_on_Intel_CPUs
#   mitigations=off l1tf=off
#   cat /sys/devices/system/cpu/vulnerabilities/*

script='/efs/benchmark/y-cruncher/src/run.py'
results='/efs/results'
template='config_pushpool.template'
digits='25m:10 50m:10 100m:10 250m:5 500m:5 1b:5 2.5b:2 5b:2 10b 25b'

# World Record constants

${script} --results ${results} --constant 'pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'e_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'e_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'euler_mascheroni_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'euler_mascheroni_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'sqrt2' --template "${template}" ${digits}
${script} --results ${results} --constant 'sqrt200' --template "${template}" ${digits}

${script} --results ${results} --constant 'golden_ratio' --template "${template}" ${digits}
${script} --results ${results} --constant 'sqrt125' --template "${template}" ${digits}

${script} --results ${results} --constant 'log2_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'log2_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'zeta3_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'zeta3_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'catalans_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'catalans_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'lemniscate' --template "${template}" ${digits}
${script} --results ${results} --constant 'Lemniscate - Series-Pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'Gamma(1d4) - AGM-Pi' --template "${template}" ${digits}
${script} --results ${results} --constant 'Gamma(1d4) - Series-Pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'Gamma(1d3) - Series-Pi' --template "${template}" ${digits}
${script} --results ${results} --constant 'Gamma(1d3) - AGM-Pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'log10_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'log10_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'Zeta(5) - BBP-Kruse' --template "${template}" ${digits}
${script} --results ${results} --constant 'Zeta(5) - Broadhurst (optimized)' --template "${template}" ${digits}

# Other constants

${script} --results ${results} --constant '2^(1d5) - Native' --template "${template}" ${digits}

${script} --results ${results} --constant '2^(1d7) - Native' --template "${template}" ${digits}

${script} --results ${results} --constant 'ArcCosh(e)' --template "${template}" ${digits}

${script} --results ${results} --constant 'ArcCoth(GoldenRatio)' --template "${template}" ${digits}

${script} --results ${results} --constant 'ArcSinh(e)' --template "${template}" ${digits}

${script} --results ${results} --constant 'ArcTanh(e^-1)' --template "${template}" ${digits}

${script} --results ${results} --constant 'ArcTanh(Pi^-1)' --template "${template}" ${digits}

${script} --results ${results} --constant 'BesselI(0,1) - Series' --template "${template}" ${digits}

${script} --results ${results} --constant 'BesselJ(0,1) - Series' --template "${template}" ${digits}

${script} --results ${results} --constant 'BronzeRatio - Native Invsqrt' --template "${template}" ${digits}
${script} --results ${results} --constant 'sqrt325' --template "${template}" ${digits}

${script} --results ${results} --constant 'Cbrt(2) - Native' --template "${template}" ${digits}
${script} --results ${results} --constant 'Cbrt(2) - Native2' --template "${template}" ${digits}

${script} --results ${results} --constant 'Cbrt(3) - Native' --template "${template}" ${digits}
${script} --results ${results} --constant 'Cbrt(3) - Native2' --template "${template}" ${digits}

${script} --results ${results} --constant 'Cos(1) - Series' --template "${template}" ${digits}
${script} --results ${results} --constant 'Cos(1) - Half Angle Formula' --template "${template}" ${digits}

${script} --results ${results} --constant 'Erf(1) - Series' --template "${template}" ${digits}
${script} --results ${results} --constant 'Erf(1) - Series-e' --template "${template}" ${digits}

${script} --results ${results} --constant 'Gamma(1d6) - AGM-Pi' --template "${template}" ${digits}
${script} --results ${results} --constant 'Gamma(1d6) - Series-Pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'Gamma(2d3) - AGM-Pi' --template "${template}" ${digits}
${script} --results ${results} --constant 'Gamma(2d3) - Series-Pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'Gamma(3d4) - AGM-Pi' --template "${template}" ${digits}
${script} --results ${results} --constant 'Gamma(3d4) - Series-Pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'Gamma(5d6) - AGM-Pi' --template "${template}" ${digits}
${script} --results ${results} --constant 'Gamma(5d6) - Series-Pi' --template "${template}" ${digits}

${script} --results ${results} --constant 'Gauss - AGM' --template "${template}" ${digits}
${script} --results ${results} --constant 'Gauss - Series' --template "${template}" ${digits}

${script} --results ${results} --constant 'Khinchin-Levy Constant' --template "${template}" ${digits}

${script} --results ${results} --constant 'log3_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'log3_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'log5_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'log5_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'log7_α' --template "${template}" ${digits}
${script} --results ${results} --constant 'log7_β' --template "${template}" ${digits}

${script} --results ${results} --constant 'Log(Pi)' --template "${template}" ${digits}

${script} --results ${results} --constant 'Log10(2)' --template "${template}" ${digits}

${script} --results ${results} --constant 'Pi^-1 - Native' --template "${template}" ${digits}

${script} --results ${results} --constant 'Sin(1) - Series' --template "${template}" ${digits}
${script} --results ${results} --constant 'Sin(1) - Triple Angle Formula' --template "${template}" ${digits}

${script} --results ${results} --constant 'Sqrt(Pi)' --template "${template}" ${digits}

${script} --results ${results} --constant 'Universal Parabolic Constant' --template "${template}" ${digits}

${script} --results ${results} --constant 'Unnormalized Fresnel C(1)' --template "${template}" ${digits}

${script} --results ${results} --constant 'Unnormalized Fresnel S(1)' --template "${template}" ${digits}

${script} --results ${results} --constant 'Zeta(2) - Chudnovsky' --template "${template}" ${digits}
${script} --results ${results} --constant 'Zeta(2) - Direct' --template "${template}" ${digits}

${script} --results ${results} --constant 'Zeta(4) - Chudnovsky' --template "${template}" ${digits}
${script} --results ${results} --constant 'Zeta(4) - Direct' --template "${template}" ${digits}

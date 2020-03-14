import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

"""
S:  Stock of susceptible
I:  Stock of infected (infectious)
R:  Stock of recovered

N:  Total population
a:  Average number of contacts per person times the probability of disease transmission (S->I).
b:  Rate of rate of recovery or death. b = 1/duration_of_infection
R0: Basic reproduction number (R0 = a / b).
    Expected number of new infections from a single infection in a population where all subjects are susceptible.

Assumptions:
* Immunity (no R -> I)

Dynamic system
dS = -aSI/N
dI = aSI/N - bI
dR = bI
"""

def dS(a, N, S, I):
    return -a*S*I/N

def dI(a, b, N, S, I):
    return a*S*I/N - b*I

def dR(b, I):
    return b*I

def dSIR(SIR, t, params):
    S,I,R = SIR
    recovery_time,R0,N = params
    b = 1./recovery_time
    a = R0 * b

    return [dS(a, N, S, I),
            dI(a, b, N, S, I),
            dR(b, I),
    ]

def solve(t, recovery_time, R0, N, I_0, R_0):
    params = [recovery_time, R0, N]
    S_0 = N-I_0-R_0
    SIR_0 = [S_0, I_0, R_0]
    SIR = odeint(dSIR, SIR_0, t, args=(params,))
    return SIR

def run_model(R0, recovery_time, N, I_0, R_0, t_end, ax):
    # Solve for some different scenarios
    t_inc = 1.
    t = np.arange(0., t_end, t_inc)

    SIR = solve(t, recovery_time, R0, N, I_0, R_0)

    # Plot result
    ax.plot(t, SIR[:,0], 'b--', label='Susceptible')
    ax.plot(t, SIR[:,1], 'r-', linewidth=2.0, label='Infected')
    ax.plot(t, SIR[:,2], 'g--', label='Recovered')
    ax.legend(loc=2)
    ax.text(3, 1.5E5, "Imax = {:.1E}\nRmax = {:.1E}\nN = {:.1E}\nI0 = {}\nR0 = {}\nRT = {} days".format(max(SIR[:,1]), max(SIR[:,2]), N, round(I_0), R0, recovery_time), bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.grid(True)

# Model Parameters
# R0 in range 2-2.5 based on analysis in China
# https://www.who.int/docs/default-source/coronaviruse/who-china-joint-mission-on-covid-19-final-report.pdf

# According to this study, patients mostly stop spreading virus 8 days after first symptoms.
# Assuming 5-14 days of spread before symptoms.
# https://www.statnews.com/2020/03/09/people-shed-high-levels-of-coronavirus-study-finds-but-most-are-likely-not-infectious-after-recovery-begins/

# Total population size
N = 10E6

# Start conditions

# 13th March, Sweden, 775 detected infections
# https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/aktuellt-epidemiologiskt-lage/
tested_positive = 775.
detection_rate = 0.5 # Just guessing here
I_0 = tested_positive / detection_rate

# Just guessing. Assuming 100 recovered
R_0 = 100.

# Number of days to run the simulation
t_end = 300.

fig, axs = plt.subplots(4, sharex='col', sharey='row', gridspec_kw={'hspace': 0, 'wspace': 0})
fig.suptitle('SIR model for COVID-19 in Sweden')

for ax in axs.flat:
    ax.set(ylabel='individuals', xlabel='days', ylim=[0, 3.2E6], xlim=[0, t_end])
    ax.label_outer()

run_model(1.5, (5+14)/2 + 8, N, I_0, R_0, t_end, axs[0])
run_model(2.0, (5+14)/2 + 8, N, I_0, R_0, t_end, axs[1])
run_model(2.5, (5+14)/2 + 8, N, I_0, R_0, t_end, axs[2])
run_model(3.0, (5+14)/2 + 8, N, I_0, R_0, t_end, axs[3])

plt.show()

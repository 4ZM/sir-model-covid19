import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

"""
S:  Stock of susceptible
I:  Stock of infected (infectious)
R:  Stock of recovered

N:  Total population
a:  Average number of contacts per person times the probability of disease
    transmission (S->I).
b:  Rate of rate of recovery or death. b = 1/duration_of_infection
R0: Basic reproduction number (R0 = a / b).
    Expected number of new infections from a single infection in a population
    where all subjects are susceptible.

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

def run_model(R0, recovery_time, N, I_0, R_0, t_end):
    t = np.arange(0., t_end, 1)
    SIR = solve(t, recovery_time, R0, N, I_0, R_0)
    return (t, SIR[:,0], SIR[:,1], SIR[:,2])

def plot(ax, t, S, I, R, y_max):
    ax.set(ylabel='individuals', xlabel='days', ylim=[0, y_max], xlim=[0, t[-1]])
    ax.plot(t, S, 'b--', label='Susceptible')
    ax.plot(t, I, 'r-', linewidth=2.0, label='Infected')
    ax.plot(t, R, 'g--', label='Recovered')
    ax.legend(loc=1)
    ax.grid(True)


if __name__ == "__main__":
    # Model Parameters
    # R0 in range 2-2.5 based on analysis in China
    # https://www.who.int/docs/default-source/coronaviruse/who-china-joint-mission-on-covid-19-final-report.pdf

    # According to this study, patients mostly stop spreading virus 8 days after first symptoms.
    # Assuming 5-14 days of spread before symptoms.
    # https://www.statnews.com/2020/03/09/people-shed-high-levels-of-coronavirus-study-finds-but-most-are-likely-not-infectious-after-recovery-begins/

    # Total population size
    N = 10E6

    # 13th March, Sweden, 775 detected infections
    # https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/aktuellt-epidemiologiskt-lage/
    tested_positive = 775
    detection_rate = 0.1 # Just guessing here
    I_0 = tested_positive / detection_rate
    R_0 = 100 # Just guessing.

    # Number of days to run the simulation
    t_end = 300

    fig, ax = plt.subplots(1)
    fig.suptitle('SIR model for COVID-19')
    t, S, I, R = run_model(2.5, 17.5, N, I_0, R_0, t_end)
    plot(ax, t, S, I, R, 3E6)
    plt.show()

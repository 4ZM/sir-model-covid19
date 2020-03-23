import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from datetime import date
from datetime import date, timedelta

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

def run_model(R0, recovery_time, N, I_0, R_0, t_min, t_max):
    t_fwd = np.arange(0., t_max, 1)
    SIR_fwd = solve(t_fwd, recovery_time, R0, N, I_0, R_0)

    t_rev = np.arange(0., t_min, -1)
    SIR_rev = solve(t_rev, recovery_time, R0, N, I_0, R_0)

    t = np.concatenate((t_rev[::-1], t_fwd))
    SIR = np.concatenate((np.flip(SIR_rev, axis=0), SIR_fwd), axis=0)
    return (t, SIR[:,0], SIR[:,1], SIR[:,2])


def real_data():
    # https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/aktuellt-epidemiologiskt-lage/
    real_date = date(2020, 3, 1)
    t_real = np.asarray([2, 5, 6, 7, 9, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23]) - 1 # March
    Ic_real = np.asarray([15, 52, 101, 140 ,248, 461, 620, 775, 992, 1059, 1167, 1279, 1423, 1623, 1746, 1934, 2016])
    return (real_date, t_real, Ic_real)

def plot(ax, t, S, I, R, t0_date, y_max):
    ax.set(ylabel='individuals', xlabel='days', ylim=[0, y_max], xlim=[t[0], t[-1]])
    ax.plot(t, S, 'b--', label='Susceptible')
    ax.plot(t, I, 'r-', linewidth=2.0, label='Infected')
    ax.plot(t, R, 'g--', label='Recovered')
    ax.grid(True)

    real_date, t_real, Ic_real = real_data()
    t_real_adjusted = t_real + (real_date - t0_date).days
    ax.plot(t_real_adjusted, 10*Ic_real, 'k*', label='Confirmed SE x 10')
    ax.legend(loc=1)

if __name__ == "__main__":
    # Model Parameters
    # R0 in range 2-2.5 based on analysis in China
    # https://www.who.int/docs/default-source/coronaviruse/who-china-joint-mission-on-covid-19-final-report.pdf

    # Total population size
    N = 10E6

    # Number of days to run the simulation
    t_min= -20
    t_max = 150

    real_date, t_real, Ic_real = real_data()
    t0_date = real_date + timedelta(days=int(t_real[-1]))
    R0 = 2.0
    D = 7 # 2-14 Incubation + 7 Recovery

    R_0 = 10*16
    I_0 = 10*Ic_real[-1] - R_0
    fig, ax = plt.subplots(1)
    fig.suptitle('SIR model for COVID-19')
    t, S, I, R = run_model(R0, D, N, I_0, R_0, t_min, t_max)

    y_max = 2.5E6

    plot(ax, t, S, I, R, t0_date, y_max)
    plt.show()

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
a:  Parameter a to the exponential distribution for incubation period.
    I.e. the average incubation period is 1/a
beta:  Average number of contacts per person times the probability of disease
    transmission (S->E).
gamma:  Rate of rate of recovery or death. b = 1/duration_of_infection
R0: Basic reproduction number (R0 = beta / gamma).
    Expected number of new infections from a single infection in a population
    where all subjects are susceptible.

Assumptions:
* Immunity (no R -> I)

Dynamic system
dS = -beta*(I/N)*S
dE = beta*SI/N - aE
dI = aE - gammaI
dR = gammaI
"""

def dS(beta, N, S, I):
    return -beta*(I/N)*S

def dE(t, beta, a, N, S, I, E):
    return beta*(I/N)*S - a*E

def dI(a, gamma, E, I):
    return a*E - gamma*I

def dR(gamma, I):
    return gamma*I

def dSEIR(SEIR, t, params):
    S,E,I,R = SEIR
    infectious_period, incubation_period, R0, N = params

    gamma = 1./infectious_period
    beta = R0 * gamma
    a = 1./incubation_period

    return [dS(beta, N, S, I),
            dE(t, beta, a, N, S, I, E),
            dI(a, gamma, E, I),
            dR(gamma, I),
    ]

def solve(t, infectious_period, incubation_period, R0, N, E_0, I_0, R_0):
    params = [infectious_period, incubation_period, R0, N]
    S_0 = N - (E_0 + I_0 + R_0)
    SEIR_0 = [S_0, E_0, I_0, R_0]
    SEIR = odeint(dSEIR, SEIR_0, t, args=(params,))
    return SEIR

def run_model(R0, infectious_period, incubation_period, N, E_0, I_0, R_0, t_min, t_max):
    t_fwd = np.arange(0., t_max, 1)
    SEIR_fwd = solve(t_fwd, infectious_period, incubation_period, R0, N, E_0, I_0, R_0)

    t_rev = np.arange(0., t_min, -1)
    SEIR_rev = solve(t_rev, infectious_period, incubation_period, R0, N, E_0, I_0, R_0)

    t = np.concatenate((t_rev[::-1], t_fwd))
    SEIR = np.concatenate((np.flip(SEIR_rev, axis=0), SEIR_fwd), axis=0)
    return (t, SEIR[:,0], SEIR[:,1], SEIR[:,2], SEIR[:,3])


def real_data():
    # https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/aktuellt-epidemiologiskt-lage/
    real_date = date(2020, 3, 1)
    t_real = np.asarray([2, 5, 6, 7, 9, 11, 12, 13, 15, 16, 17, 18, 19]) - 1 # March
    Ic_real = np.asarray([15, 52, 101, 140 ,248, 461, 620, 775, 992, 1059, 1167, 1279, 1423])
    return (real_date, t_real, Ic_real)

def plot(ax, t, S, E, I, R, t0_date, y_max):
    ax.set(ylabel='individuals', xlabel='days', ylim=[0, y_max], xlim=[t[0], t[-1]])
    ax.plot(t, S, 'b--', label='Susceptible')
    ax.plot(t, E, 'r-.', linewidth=2.0, label='Exposed')
    ax.plot(t, I, 'r-', linewidth=2.0, label='Infectious')
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
    t_max = 10

    real_date, t_real, Ic_real = real_data()
    t0_date = real_date + timedelta(days=int(t_real[-1]))
    R0 = 2.0

    infectious_period = 5

    # https://www.sciencedaily.com/releases/2020/03/200317175438.htm
    # "median incubation period for COVID-19 is just over five days "
    incubation_period = 7

    R_0 = 10*16
    I_0 = 10*Ic_real[-1] - R_0
    E_0 = 2*I_0

    fig, ax = plt.subplots(1)
    fig.suptitle('SIR model for COVID-19')
    t, S, E, I, R = run_model(R0, infectious_period, incubation_period, N, E_0, I_0, R_0, t_min, t_max)

    y_max = 1E5
    plot(ax, t, S, E, I, R, t0_date, y_max)
    plt.show()

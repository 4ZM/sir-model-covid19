from datetime import date
import numpy as np

def data_sweden():
    # https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/aktuellt-epidemiologiskt-lage/
    t0_date = date(2020, 3, 1)

    # days since t0 date
    march = np.asarray([2, 5, 6, 7, 9, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]) - 1
    april = np.asarray([1, 2]) + march[-1]

    I_march = np.asarray([15, 52, 101, 140 ,248, 461, 620, 775, 992, 1059, 1167, 1279, 1423, 1623, 1746, 1934, 2016, 2272, 2510, 2806, 3069, 3447, 3700, 4028, 4435])
    I_april = np.asarray([4947, 5466])

    return (t0_date, np.concatenate((march, april)), np.concatenate((I_march, I_april)))

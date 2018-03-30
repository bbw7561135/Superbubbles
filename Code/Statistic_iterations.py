##------------------------##
# Librairies and functions #
##------------------------##
import matplotlib.pyplot as plt
import numpy
import scipy.integrate as integrate
import astropy.units as units
import os
import pickle
import naima
from statistics import mean, stdev
from naima.models import PionDecay, TableModel
from Functions import *
from Functions_CR import *
from Functions_SB import *
from Functions_gamma import *

# Physical constants and conversion factors
from Physical_constants import *
from Conversion_factors import *
from Parameters_SB import *

    # IRAP
os.chdir('/Users/stage/Documents/Virginie/Superbubbles/Files/stat_SN/Test/')
pathfigure_gamma = '/Users/stage/Documents/Virginie/Superbubbles/figures/stat_SN/Gamma_emission/Test/'
#pathfigure_CR = '/Users/stage/Documents/Virginie/Superbubbles/figures/stat_SN/CR/1/'

    # Home
#os.chdir('/home/vivi/Documents/Master_2/Superbubbles/Files/stat_SN/Test/')
#pathfigure_gamma = '/home/vivi/Documents/Master_2/Superbubbles/figures/stat_SN/Gamma_emission/Test/'
#pathfigure_CR = '/home/vivi/Documents/Master_2/Superbubbles/figures/stat_SN/CR/2/'

## ======= ##
# Statistic #
## ======= ##

    # Number of iterations
nit = 1

    # Parameters for the cosmic rays

        # Energy
Emin_CR = 1            # minimum kinetic energy: Emin = 1GeV
Emax_CR = 1*PeV2GeV    # minimum kinetic energy: Emax = 1PeV in GeV

        # Power-law distribution of the cosmic rays (GeV^-1 cm^-3)
p0 = 10             # normalization constant (GeV/c)
alpha = 2.0         # exponent of the power-law distribution

        # Diffusion coefficient of the cosmic rays (cm^2 s^-1)
delta = 1.0/3       # exponent of the power-law of the diffusion coefficient
D0 = 1e28           # diffusion coefficient at 10 GeV/c in cm^2 s^-1

    # Which zone for the Computation
zones = [2]

    # Statistic on the spectrum
flux_it_1 = []      # total gamma luminosity from 100 MeV to 100 GeV
flux_it_2 = []      # total gamma luminosity from 100 GeV to 100 TeV
flux_it = []        # total gamma luminosity from 100 MeV to 100 TeV
time = []           # total time array for each iteration

    # Initialization
figure_number = 1

with open('Statistic', 'wb') as stat_write:

        # Fix time array (yr)
    t0min = 3                   # Myr
    t0max = 37                  # Myr

    tmin = t0min/yr26yr         # yr
    tmax = (t0max + 1)/yr26yr    # yr
    number_bin_t = 300000
    time = numpy.linspace(tmin, tmax, number_bin_t)

        # Energy of the gamma photons (GeV)
    Emin_gamma = 100 * MeV2GeV            # 100 MeV (GeV)
    Emax_gamma = 100 * TeV2GeV            # 100 TeV (GeV)
    Esep = 100      # in GeV

        ##----------##
        # Iterations #
        ##----------##

    for i in range (nit):

            # SN explosion time
        n = 3             # number of massive stars in the OB association
        t0 = random_SN(3, 37, n)/yr26yr
        t0 = sorted(t0)

        flux_1, flux_2, flux, flux_units = data(t0, time, Emin_CR, Emax_CR, Emin_gamma, Emax_gamma, Esep, p0, alpha, D0, delta, zones)
        """
        flux_it_1.append(flux_1)
        flux_it_2.append(flux_2)
        flux_it.append(flux)

            # spectral index
        indE = 10       # which energy that the spectral index would be computed
        spectral_index(indE, zones, pathfigure_gamma, i, figure_number)

        print('end of the iteration')

    flux_it_1 = numpy.asarray(flux_it_1)
    flux_it_2 = numpy.asarray(flux_it_2)
    flux_it = numpy.asarray(flux_it)
    pickle.dump(flux_it_1, stat_write)
    pickle.dump(flux_it_2, stat_write)
    pickle.dump(flux_it, stat_write)
"""
"""
with open('Statistic', 'rb') as stat_load:

    time = pickle.load(stat_load)
    print(time.shape)
    Lum_it_1 = pickle.load(stat_load)
    print(Lum_it_1.shape)
    Lum_it_2 = pickle.load(stat_load)
    print(Lum_it_2.shape)
    Lum_it = pickle.load(stat_load)
    print(Lum_it.shape)

    t_tot = []
    Lum_tot_1 = []
    Lum_tot_2 = []
    Lum_tot = []
    index_it = []
    n = 0
    index.append(n)

    for i in range (nit):

        nt = len(time[i])
        t = time[i]
        Lum_t0_1 = Lum_it_1[i]
        Lum_t0_2 = Lum_it_2[i]
        Lum_t0 = Lum_it[i]

        for j in range (nt):

            t_tot.append(t[j])
            Lum_tot_1.append(Lum_t0_1[j])
            Lum_tot_2.append(Lum_t0_2[j])
            Lum_tot.append(Lum_t0[j])
            n += 1

        if i != nit - 1:
            index_it.append(n)  # recording the index of each iteration

    sort_index = numpy.argsort(t_tot)
    t_tot = sorted(t_tot)
    #Lum_tot_1 = numpy.asarray(Lum_tot_1)
    #Lum_tot_2 = numpy.asarray(Lum_tot_2)
    #Lum_tot = numpy.asarray(Lum_tot)
    #Lum_tot_1 = Lum_tot_1[sort_index]
    #Lum_tot_2 = Lum_tot_2[sort_index]
    #Lum_tot = Lum_tot[sort_index]
    """

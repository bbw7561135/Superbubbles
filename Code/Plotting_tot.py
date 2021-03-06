"""
It plots the gamma-ray luminosities in the HE and VHE energy ranges and the spectral index in both energy ranges for one case.

All the parameters must be given in the Parameters_system.

Make sure that you have already run the code 'Plotting.py' to have the concatenisation of the data set.
"""

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
from naima.models import PionDecay, TableModel
from Functions import *
from Functions_CR import *
from Functions_SB import *
from Functions_gamma import *

# Physical constants and conversion factors
from Physical_constants import *
from Conversion_factors import *
from Parameters_system import *

##====##
# Path #
##====##

    # you need to change it
pathfigure_gamma = '/Users/stage/Documents/Virginie/Superbubbles/figures/Parametric_studies/percentage/20/Gamma_emission/'

## ======================================= ##
# Statistic for a high number of iterations #
## ======================================= ##

    # Initialization
figure_number = 1

    ## ------- ##
    # Load data #
    ## ------- ##

os.chdir('/Users/stage/Documents/Virginie/Superbubbles/Files/Parametric_studies/percentage/20/')

with open('Total', 'rb') as iteration_write:

    Lum_HESS_it = pickle.load(iteration_write)
    nit_tot = len(Lum_HESS_it)
    Lum_Fermi_it = pickle.load(iteration_write)
    Lum_it = pickle.load(iteration_write)
    Gamma_HESS_it = pickle.load(iteration_write)
    Gamma_GeV_it = pickle.load(iteration_write)
    Gamma_MeV_it = pickle.load(iteration_write)
    Lum_pwn_it = pickle.load(iteration_write)
    Lum_psr_it = pickle.load(iteration_write)
    tsn_it = pickle.load(iteration_write)
    nsn_it = pickle.load(iteration_write)

os.chdir('/Users/stage/Documents/Virginie/Superbubbles/Files/Parametric_studies/stars/100/')

with open('CRbackground', 'rb') as CR_write:

    Lum_CRb = pickle.load(CR_write)
    Lum_HESS_CRb = pickle.load(CR_write)
    Lum_Fermi_CRb = pickle.load(CR_write)

    ##---------------------------##
    # Mean and standard deviation #
    ##---------------------------##

        # Initialization

            # Mean
Lum_HESS_mean = numpy.zeros(number_bin_t)               # from 1 TeV to 10 TeV
Lum_Fermi_mean = numpy.zeros(number_bin_t)              # from 100 MeV to 100 GeV
Lum_mean = numpy.zeros(number_bin_t)                    # from 100 MeV to 100 TeV
Gamma_HESS_mean = numpy.zeros(number_bin_t)             # photon spectral index from 1 TeV to 10 TeV
Gamma_GeV_mean = numpy.zeros(number_bin_t)              # photon spectral index from 1 GeV to 10 GeV
Gamma_MeV_mean = numpy.zeros(number_bin_t)              # photon spectral index from 100 MeV to 1 GeV
Lum_pwn_mean = numpy.zeros(number_bin_t)                # TeV emission of PWNe
Lum_psr_mean = numpy.zeros(number_bin_t)                # GeV emission of PSRs

            # Standard deviation
Lum_HESS_std = numpy.zeros(number_bin_t)                # from 1 TeV to 10 TeV
Lum_Fermi_std = numpy.zeros(number_bin_t)               # from 100 MeV to 100 GeV
Lum_std = numpy.zeros(number_bin_t)                     # from 100 MeV to 100 TeV
Gamma_HESS_std = numpy.zeros(number_bin_t)              # photon spectral index from 1 TeV to 10 TeV
Gamma_GeV_std = numpy.zeros(number_bin_t)               # photon spectral index from 1 GeV to 10 GeV
Gamma_MeV_std = numpy.zeros(number_bin_t)               # photon spectral index from 100 MeV to 1 GeV

for j in range (number_bin_t):

    Lum_HESS = Lum_HESS_it[:, j]

    Lum_Fermi = Lum_Fermi_it[:, j]

    Lum = Lum_it[:, j]

    Gamma_HESS = Gamma_HESS_it[:, j]

    Gamma_GeV = Gamma_GeV_it[:, j]

    Gamma_MeV = Gamma_MeV_it[:, j]

    Lum_pwn = Lum_pwn_it[:, j]
    Lum_pwn = Lum_pwn[numpy.where(Lum_pwn > 0.0)[0]]

    Lum_psr = Lum_psr_it[:, j]
    Lum_psr = Lum_psr[numpy.where(Lum_psr > 0.0)[0]]

    Lum_HESS_mean[j] = numpy.mean(Lum_HESS)
    Lum_Fermi_mean[j] = numpy.mean(Lum_Fermi)
    Lum_mean[j] = numpy.mean(Lum)
    Gamma_HESS_mean[j] = numpy.mean(Gamma_HESS)
    Gamma_GeV_mean[j] = numpy.mean(Gamma_GeV)
    Gamma_MeV_mean[j] = numpy.mean(Gamma_MeV)
    Lum_pwn_mean[j] = 10**(numpy.mean(numpy.log10(Lum_pwn)))
    Lum_psr_mean[j] = 10**(numpy.mean(numpy.log10(Lum_psr)))

    Lum_HESS_std[j] = numpy.std(Lum_HESS)
    Lum_Fermi_std[j] = numpy.std(Lum_Fermi)
    Lum_std[j] = numpy.std(Lum)
    Gamma_HESS_std[j] = numpy.std(Gamma_HESS)
    Gamma_GeV_std[j] = numpy.std(Gamma_GeV)
    Gamma_MeV_std[j] = numpy.std(Gamma_MeV)

Lum_HESS_mean = numpy.nan_to_num(Lum_HESS_mean)
Lum_HESS_std = numpy.nan_to_num(Lum_HESS_std)
Lum_HESS_pst = Lum_HESS_mean + Lum_HESS_std
Lum_HESS_mst = Lum_HESS_mean - Lum_HESS_std
Lum_HESS_mst = numpy.nan_to_num(Lum_HESS_mst)
ind0 = numpy.where(Lum_HESS_mst < 0)[0]
Lum_HESS_mst[ind0] = numpy.zeros(len(ind0))

Lum_Fermi_mean = numpy.nan_to_num(Lum_Fermi_mean)
Lum_Fermi_std = numpy.nan_to_num(Lum_Fermi_std)
Lum_Fermi_pst = Lum_Fermi_mean + Lum_Fermi_std
Lum_Fermi_mst = Lum_Fermi_mean - Lum_Fermi_std
Lum_Fermi_mst = numpy.nan_to_num(Lum_Fermi_mst)
ind0 = numpy.where(Lum_Fermi_mst < 0)[0]
Lum_Fermi_mst[ind0] = numpy.zeros(len(ind0))

Lum_mean = numpy.nan_to_num(Lum_mean)
Lum_std = numpy.nan_to_num(Lum_std)
Lum_pst = Lum_mean + Lum_std
Lum_mst = Lum_mean - Lum_std
Lum__mst = numpy.nan_to_num(Lum_mst)
ind0 = numpy.where(Lum_mst < 0)[0]
Lum_mst[ind0] = numpy.zeros(len(ind0))

Gamma_HESS_pst = Gamma_HESS_mean + Gamma_HESS_std
Gamma_HESS_mst = Gamma_HESS_mean - Gamma_HESS_std
ind0 = numpy.where(Gamma_HESS_mst < 0)[0]
Gamma_HESS_mst[ind0] = numpy.zeros(len(ind0))

Gamma_GeV_pst = Gamma_GeV_mean + Gamma_GeV_std
Gamma_GeV_mst = Gamma_GeV_mean - Gamma_GeV_std
ind0 = numpy.where(Gamma_GeV_mst < 0)[0]
Gamma_GeV_mst[ind0] = numpy.zeros(len(ind0))

Gamma_MeV_pst = Gamma_MeV_mean + Gamma_MeV_std
Gamma_MeV_mst = Gamma_MeV_mean - Gamma_MeV_std
ind0 = numpy.where(Gamma_MeV_mst < 0)[0]
Gamma_MeV_mst[ind0] = numpy.zeros(len(ind0))


    # Plot
label_std = 'none'
sym_mean = ['', '', '']
linestyle_mean = ['-.', '-', 'dashed']
xlabel = 'Time [Myr]'
text = ''
Title = ''
xmin = tmin * yr26yr - 0.5
xmax = tmax * yr26yr + 0.5
ymin = 1e30
ymax = 1e37

        # Gamma luminosity of the superbubble

            # HESS energy range
label_mean = ['VHE CRs', 'PWNe', 'CRs background']
color_mean = ['cornflowerblue', 'green', 'darkblue']
color_std = ['cornflowerblue', 'cornflowerblue']
y_mean = [Lum_HESS_mean, Lum_pwn_mean, Lum_HESS_CRb]
ylabel_HESS = '$L_\gamma$ [erg s$^{-1}$] (1 TeV - 10 TeV)'

semilog_plot(figure_number, 3, t6, y_mean, xlabel, ylabel_HESS, sym_mean, linestyle_mean, color_mean, xmin, xmax, ymin, ymax, label_name = label_mean)
plt.fill_between(t6, Lum_HESS_pst, Lum_HESS_mst, color = 'cornflowerblue', alpha = '0.25')
plt.savefig(pathfigure_gamma+'Mean_gamma_emission_HESS.pdf')

figure_number += 1

            # Fermi energy range
label_mean = ['HE CRs', 'PSRs', 'CRs background']
color_mean = ['orangered', 'orange', 'maroon']
y_mean = [Lum_Fermi_mean, Lum_psr_mean, Lum_Fermi_CRb]
ylabel_HESS = '$L_\gamma$ [erg s$^{-1}$] (100 MeV - 100 GeV)'

semilog_plot(figure_number, 3, t6, y_mean, xlabel, ylabel_HESS, sym_mean, linestyle_mean, color_mean, xmin, xmax, ymin, ymax, label_name = label_mean)
plt.fill_between(t6, Lum_Fermi_pst, Lum_Fermi_mst, color = 'orangered', alpha = '0.25')
plt.savefig(pathfigure_gamma+'Mean_gamma_emission_Fermi.pdf')

figure_number += 1

        # Spectral index
label = 'none'
sym = ''
linestyle = '-.'
ymin = 0.0
ymax = 3.5

            # HESS energy range
y = Gamma_HESS_mean
color = 'cornflowerblue'
ylabel_HESS = '$\Gamma_{ph}$ (1 TeV - 10 TeV)'

plot(figure_number, 1, t6, y, xlabel, ylabel_HESS, sym, linestyle, color, xmin, xmax, ymin, ymax)
plt.fill_between(t6, Gamma_HESS_pst, Gamma_HESS_mst, color = 'cornflowerblue', alpha = '0.25')
plt.savefig(pathfigure_gamma+'Photon_index_HESS.pdf')

figure_number += 1

            # 1 GeV to 10 GeV
y = Gamma_GeV_mean
color = 'orangered'
ylabel_GeV = '$\Gamma_{ph}$ (1 GeV - 10 GeV)'

plot(figure_number, 1, t6, y, xlabel, ylabel_GeV, sym, linestyle, color, xmin, xmax, ymin, ymax)
plt.fill_between(t6, Gamma_GeV_pst, Gamma_GeV_mst, color = 'orangered', alpha = '0.25')
plt.savefig(pathfigure_gamma+'Photon_index_GeV.pdf')

figure_number += 1

    ## ----------- ##
    # Probabilities #
    ## ----------- ##

Proba_HESS, Proba_HESS_CR, Proba_Fermi, Proba_Fermi_CR, Proba_pwn_psr = probability(Lum_HESS_it, Lum_Fermi_it, Lum_pwn_it, Lum_psr_it, Lum_HESS_CRb, Lum_Fermi_CRb, nit_tot, number_bin_t)

ymin = 0.0
ymax = 1.0
sym = ['', '', '', '', '']
linestyle = ['-', '-', '-', '-', '-']
color = ['green', 'blue', 'orange', 'red', 'violet']
label = ['VHE CRs + PWNe', 'only VHE CRs', 'HE CRs + PSRs', 'only HE CRs', 'no PWN - no PSR']
y = [Proba_HESS, Proba_HESS_CR, Proba_Fermi, Proba_Fermi_CR, Proba_pwn_psr]

plot(figure_number, 5, t6, y, xlabel, ylabel_GeV, sym, linestyle, color, xmin, xmax, ymin, ymax, label_name = label)
plt.savefig(pathfigure_gamma+'Probabilities.pdf')

plt.show()

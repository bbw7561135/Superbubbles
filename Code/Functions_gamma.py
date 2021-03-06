##------------------------##
# Librairies and functions #
##------------------------##
import matplotlib.pyplot as plt
import numpy
import scipy.integrate as integrate
import astropy.units as units
from astropy.io import ascii
import os
import pickle
import naima
from naima.models import PionDecay, TableModel
from Functions import *
from Functions_CR import *
from Functions_SB import *

## --------------------------------------- ##
# Physical constants and conversion factors #
## --------------------------------------- ##

from Physical_constants import *
from Conversion_factors import *
from Parameters_system import *

##---------##
# Functions #
##---------##

def cosmicray_lis(ekin):
    """
    Return the cosmic rays spectrum from a table of kinetic energy.

    Inputs:
        ekin    :   kinetic energy array (GeV)

    Output:
        n_recast:   cosmic rays spectrum interpolated from file (GeV^-1 cm^-3)
    """
        # Physical constants
    mpgev = mp * MeV2GeV     # GeV
    clight = cl * cm2m       # m/s

        # Load LIS data from Boschini-2017 papers
    data = ascii.read('/Users/stage/Documents/Virginie/Superbubbles/Code/CosmicRayLocal.txt',data_start=1)

        # Convert from proton/m2/s/sr/GeV into proton/GeV/cm3 by multiplying by 4pi/v and 1e6 for m-3 to cm-3
    ek_lis = numpy.asarray(data['Ekin'])
    lorentz = 1.0+ek_lis/mpgev
    beta = numpy.sqrt(1.0-1.0/numpy.power(lorentz,2))
    n_lis = numpy.asarray(data['Flux']*4.0*numpy.pi/beta/clight) * (cm2m)**3  # proton/GeV/cm3

        # Recast on input grid
    lis_itp = lambda e : 10.0**(loglog_interpolation(ek_lis,n_lis)(numpy.log10(e)))
    nk = ekin.size
    n_recast = numpy.zeros(nk)

    for i in range(nk):
            # Interpolate LIS spectrum over the input LIS range
            #...and extend with power-law interpolation of index -2.7 above the range (see figure 4 of AMS-02 2015 paper)
        n_recast[i] = lis_itp(ekin[i]) if ekin[i] <= ek_lis.max() else n_lis[-1]*(ekin[i]/ek_lis[-1])**(-2.7)  # proton/GeV/cm3

    return n_recast

def pwn_emission(tsn,tsb):

   """
   Return the TeV emission (in the HESS energy range (1 TeV to 10 TeV) of a pulsar wind nebula
	  From HESS PWNe paper of 2018

   Inputs:
	  tsn		:	time of the SN explosion (yr)
	  tsb		:	age of the superbubble (yr)

   Output:
	  pwn_lum	:	TeV emission of a PWN (erg s^-1)
   """
   # Pulsar parameters from table A1
   n=3  		# braking index
   tau0=5e2  	# Initial spin-down time scale in yrs
   Edot0=2e39  # Initial spin-down power in erg/s

   # Age of pulsar
   t=tsb-tsn  	# in yrs

   # Compute spin-down power at this time ()
   Edot=Edot0*(1.0+t/tau0)**((n+1)/(1-n))  # in erg/s

   # Compute 1-10TeV luminosity from fitted relation of table 6 with age limit at 2e5 yr
   logE=numpy.log10(Edot/1e36)
   logL=33.22+0.59*logE
   pwn_lum= 10**logL if t < 2e5 else 0.0  # in erg/s

   return pwn_lum

def psr_emission(tsn,tsb):

   """
   Return the GeV emission (in the Fermi energy range (0.1 GeV to 100 GeV) from a pulsar
	  From Fermi-LAT 2PC paper with pulsar initial spin-down parameters from HESS PWNe paper

   Inputs:
        tsn		:	time of the SN explosion (yr)
        tsb		:	age of the superbubble (yr)

   Output:
        psr_lum	:	GeV emission of a pulsr (erg s^-1)
   """

   # Pulsar parameters from table A1
   n=3  		# braking index
   tau0=5e2  	# Initial spin-down time scale in yrs
   Edot0=2e39  # Initial spin-down power in erg/s

   # Age of pulsar
   t=tsb-tsn  	# in yrs

   # Compute spin-down power at this time ()
   Edot=Edot0*(1.0+t/tau0)**((n+1)/(1-n))  # in erg/s

   # Compute 0.1-100GeV luminosity from heuristic relation in 2PC with power limit at 1e34 erg/s
   # (supported by simulation by Kalapotharakos-2018)
   psr_lum = numpy.sqrt(1e33*Edot) if Edot > 1e34 else 0.0 # in erg/s

   return psr_lum

def luminosity(lum_energy, energy):

    """
    Return the luminosity in a range of energy

    Inputs:
        lum_energy 	:   intrinsic luminosity array per energy (erg/s/eV)
        energy      :   range of energy in which we will compute the luminosity (eV)

    Output:
        lum         :   luminosity (erg s^-1)
    """
    lum = integrate.trapz(lum_energy, energy)
    lum = numpy.nan_to_num(lum)

    return lum

def spectral_index(Emin, Emax, lum_ph_min, lum_ph_max):

    """
    Return the spectral index at an energy

    Inputs:
        Emin        :   minimum energy of the range (GeV)
        Emax        :   maximum energy of the range (GeV)
        lum_ph_min  :   intrinsic differential luminosity in photons at Emin (ph/eV/s)
        lum_ph_max  :   intrinsic differential luminosity in photons at Emax (ph/eV/s)

    Output:
        Gamma       :   photon spectral index
    """

    Emin = Emin * GeV2eV
    Emax = Emax * GeV2eV

    return -(numpy.log(lum_ph_max) - numpy.log(lum_ph_min))/(numpy.log(Emax) - numpy.log(Emin))

def data(correction_factor, t0, t, zones):

    """
    Returns 6 importants quantities:
        luminosity in the all energy range
        photon spectral index
        number of pulsar wind nebula
        TeV emission of PWNe
        GeV emission of PSRs
        number of remained OB stars

    Inputs:
        correction_factor   :   correction factor for the radius of the SB
        t0                  :   (sorted) array of the SN explosion times (yr)
        t                   :  	time array (yr)
        zones               :   which zone do you want to compute (1: cavity of the SB, 2: supershell and 3: outside)

    Outputs:
        Lumtot_sn           :   luminosity in the whole energy range (erg s^-1)
        Flux_sn             :   intrinsic differential luminosity in the whole energy range (eV^-1 s^-1)
	    Lum_pwn_sn		    :	TeV emission of PWNe (erg s^-1)
        Lum_psr_sn		    :	GeV emission of PSRs (erg s^-1)
        nob                 :   number of remained OB stars inside the OB association
        R_sb                :   radius of the superbubble (pc)
        V_sb                :   velocity of the superbubble (km/s)
        M_s                 :   mass in the shell (solar masses)
        n_s                 :   density in the shell (cm^-3)
    """

        ## ====================================================== ##
        # power-law distribution of the cosmic rays (GeV^-1 cm^-3) #
        ## ====================================================== ##
            # N(p) = N0 * (p/p0)^(-alpha)
            # N(E) = N0/c * ((E^2 + 2*mp*c^2*E)^(-(1+alpha)/2) * (E + mp*c^2)/((E0^2 + 2*mp*E0)^(-alpha/2)) d^3(r)
    N_E = power_law_distribution(ECR)

        ## =============================== ##
        # diffusion coefficient (cm^2 s^-1) #
        ## =============================== ##
            # D(p) = D0 * (p/p0)^(-delta)
            # D(E) = D0 * (E^2 + 2*mpg*E)^(delta/2) * 1/p0^delta
    D = diffusion_coefficient(ECR)

        ## =============================================================== ##
        # Computation of gamma luminosity in each range of energy(erg s^-1) #
        ## =============================================================== ##

            # Initialization
                # length of the arrays
    nt0 = len(t0)
    nt = len(t)

                # time evolution of the number of OB-stars
    nob = Nob * numpy.ones(nt)

                # Gamma luminosity (erg s^-1)
    for zone in (zones):

        if zone == 1:       # in the SB

            Lumsb_sn = numpy.zeros(nt)              # 100 MeV to 100 TeV

        elif zone == 2:     # in the supershell

            Lumshell_sn = numpy.zeros(nt)           # 100 MeV to 100 TeV

        else:               # outside the SB

            Lumout_sn = numpy.zeros(nt)             # 100 MeV to 100 TeV

            # Total

    Lumtot_sn = numpy.zeros(nt)             # 100 MeV to 100 TeV

                # intrinsic diferential luminosity (eV^-1 s^-1)
    Flux_sn = numpy.zeros((nt, number_bin_E))       # 100 MeV to 100 TeV


        # TeV and GeV emission of PWN and PSR
    Lum_pwn_sn = numpy.zeros(nt)
    Lum_psr_sn = numpy.zeros(nt)

        # Parameters of the superbubble
    R_sb = numpy.zeros(nt)
    V_sb = numpy.zeros(nt)
    M_s = numpy.zeros(nt)
    n_s = numpy.zeros(nt)

    for i in range (nt0):                                                       # for each SN explosions

            # Time array (yr)
        t6 = t0[i] * yr26yr  # in Myr
        Rsb = radius_velocity_SB(t6)[0]         # outer radius of the superbubble (Weaver model) (pc)
        Rsb = correction_factor * Rsb           # outer radius of the superbubble (corrected) (pc)
        tdiffmax = diffusion_time(Rsb, D[0])    # maximal diffusion time scale (yr)
        tmin = t0[i]                            # only when the SN occurs and the high-energy particles enter the supershell (yr)
        tmax = tmin + 10*tdiffmax      # almost all the CR have left the superbubble (yr)
        number_bin_t = 200
        time = numpy.logspace(numpy.log10(tmin), numpy.log10(tmax), number_bin_t)
        time6 = time * yr26yr   # Myr

            # Initialization

                # only time corresponding to the time array
        indt = numpy.where((t >= tmin) & (t <= tmax))[0]    # for the gamma luminosity
        indtob = numpy.where(t >= t0[i])[0]                 # number of remained ob stars

                # gamma luminosity (erg s^-1)
        for zone in (zones):

            if zone == 1:                       # in the SB

                Lum_t_sb = numpy.zeros(number_bin_t)

            elif zone == 2:                     # in the supershell

                Lum_t_shell = numpy.zeros(number_bin_t)

            else:                               # outside the SB

                Lum_t_out = numpy.zeros(number_bin_t)

        Lum_t_tot = numpy.zeros(number_bin_t)

        Flux = numpy.zeros((number_bin_t, number_bin_E))

        Lum_pwn_t = numpy.zeros(number_bin_t)
        Lum_psr_t = numpy.zeros(number_bin_t)
        Rsb_t = numpy.zeros(number_bin_t)
        Vsb_t = numpy.zeros(number_bin_t)
        Ms_t = numpy.zeros(number_bin_t)
        ns_t = numpy.zeros(number_bin_t)

        for j in range (number_bin_t):                                          # for each time step

                # Initialization
            t6 = time6[j]           	# 10^6 yr
            t7 = t6 * s6yr27yr      	# 10^7 yr
            delta_t = time[j] - time[0]
            SB = False  # we do not compute inside the SB

                # Parameters of the SB
            Rsb_t[j], Vsb_t[j] = radius_velocity_SB(t6)                                 # radius of the SB (pc)
            Rsb_t[j] = correction_factor * Rsb_t[j]                                     # correction of the radius
            Rsb = Rsb_t[j]
            Vsb = Vsb_t[j]
            Msb, Mswept = masses(t7, Rsb)                                               # swept-up and inner masses (solar masses)
            Ms_t[j] = Mswept - Msb                                                      # mass in the shell (solar masses)
            ns, hs = density_thickness_shell_percentage(percentage, Rsb, Mswept, Msb)  # thickness (pc) and density (cm^-3) of the shell
            #ns, hs = density_thickness_shell(Vsb, Mswept, Msb, Rsb)                     # thickness (pc) and density (cm^-3) of the shell
            ns_t[j] = ns

                # For each zones
            for zone in (zones):

                if zone == 1:                                                   # inside the SB

                    SB = True   # we compute the interior of the SB

                        # distance array (pc)
                    rmin = 0.01                 # minimum radius (pc)
                    rmax = Rsb-hs               # maximum radius (pc)
                    number_bin_r = 15           # number of bin for r from 0 to Rsb-hs
                    r = numpy.logspace(numpy.log10(rmin), numpy.log10(rmax), number_bin_r)    # position (pc)

                        # Density of gas (cm^-3)
                    nsb = profile_density_temperature(t7, r, Rsb)[1]
                    ngas = nsb * 1/units.cm**3

                        # Particles distribution (GeV^-1)
                    r_in = 0
                    r_out = r[0]
                    N_part = shell_particles(r_in, r_out, N_E, D, delta_t) * 1/units.GeV

                    if numpy.asarray(N_part).all() == 0:
                        continue

                        # For all the range of energy (100 MeV to 100 TeV)
                            # intrisic differential luminosity (eV^-1 s^-1)
                    model = TableModel(E_CR, N_part, amplitude = 1)
                    PD = PionDecay(model, nh = ngas[0], nuclear_enhancement = True, useLUT = False)
                    flux_PD = PD.flux(spectrum_energy, distance = 0 * units.pc)
                    flux_PD = numpy.nan_to_num(numpy.asarray(flux_PD))
                    Flux[j] += flux_PD

                            # Gamma luminosity (erg s^-1)
                    lum_energy = flux_PD * spectrum_erg          # erg s^-1 eV^-1

                    Lum = luminosity(lum_energy, spectrum_ev)
                    Lum_t_sb[j] += Lum

                    for k in range (1, number_bin_r):   # for each radius inside the SB

                            # Particles distribution (GeV^-1)
                        r_in = r_out
                        r_out = r[k]
                        N_part = shell_particles(r_in, r_out, N_E, D, delta_t) * 1/units.GeV

                        if numpy.asarray(N_part).all() == 0:
                            continue

                            # For all the range of energy (100 MeV to 100 TeV)
                                # intrisic differential luminosity (eV^-1 s^-1)
                        model = TableModel(E_CR, N_part, amplitude = 1)
                        PD = PionDecay(model, nh = ngas[k], nuclear_enhancement = True, useLUT = False)
                        flux_PD = PD.flux(spectrum_energy, distance = 0 * units.pc)
                        flux_PD = numpy.nan_to_num(numpy.asarray(flux_PD))
                        Flux[j] += flux_PD

                                # Gamma luminosity (erg s^-1)
                        lum_energy = flux_PD * spectrum_erg          # erg s^-1 eV^-1
                        Lum = luminosity(lum_energy, spectrum_ev)
                        Lum_t_sb[j] += Lum

                elif zone == 2:                                                 # in the supershell

                        # Density of gas (cm^-3)
                    ngas = ns * 1/units.cm**3

                        # Particles distribution (GeV^-1)
                    r_in = Rsb - hs     # in pc
                    r_out = Rsb         # in pc
                    N_part = shell_particles(r_in, r_out, N_E, D, delta_t) * 1/units.GeV

                    if numpy.asarray(N_part).all() == 0:
                        continue

                        # For all the range of energy (100 MeV to 100 TeV)
                            # intrisic differential luminosity (eV^-1 s^-1)
                    model = TableModel(E_CR, N_part, amplitude = 1)
                    PD = PionDecay(model, nh = ngas, nuclear_enhancement = True, useLUT = False)
                    flux_PD = PD.flux(spectrum_energy, distance = 0 * units.pc)
                    flux_PD = numpy.nan_to_num(numpy.asarray(flux_PD))
                    Flux[j] += flux_PD

                            # Gamma luminosity (erg s^-1)
                    lum_energy = flux_PD * spectrum_erg          # erg s^-1 eV^-1
                    Lum = luminosity(lum_energy, spectrum_ev)
                    Lum_t_shell[j] += Lum

                else:                                                           # outside the SB

                        # Density of gas
                    ngas = n0 * 1/units.cm**3

                        # Distribution of particles (GeV^-1)
                    N_part = inf_particles(Rsb, N_E, D, delta_t) * 1/units.GeV

                        # For all the range of energy (100 MeV to 100 TeV)
                            # intrisic differential luminosity (eV^-1 s^-1)
                    model = TableModel(E_CR, N_part, amplitude = 1)
                    PD = PionDecay(model, nh = ngas, nuclear_enhancement = True, useLUT = False)
                    flux_PD = PD.flux(spectrum_energy, distance = 0 * units.pc)
                    flux_PD = numpy.nan_to_num(numpy.asarray(flux_PD))

                            # Gamma luminosity (erg s^-1)
                    lum_energy = flux_PD * spectrum_erg          # erg s^-1 eV^-1

                    Lum = luminosity(lum_energy, spectrum_ev)
                    Lum_t_out[j] += Lum

            if SB:  # if we compute what happens inside the SB

                Lum_t_tot[j] = Lum_t_sb[j] + Lum_t_shell[j]

            else:   # the only relevant gamma luminosity is the one of the supershell

                Lum_t_tot[j] = Lum_t_shell[j]

            Lum_pwn_t[j] += pwn_emission(t0[i], time[j])
            Lum_psr_t[j] += psr_emission(t0[i],time[j])

            # Interpolation

                # number of OB stars
        for l in (indtob):
            nob[l] -= 1

                # Pulsar wind nebula

        #for l in (indt_pwn):
        #    n_pwn_tot[l] += 1

                # Gamma luminosity + spectral index
        """
        Title_HESS = 'Gamma emission from 1 TeV to 10 TeV (t0 = %.2e yr)'%t0[i]
        Title = 'Gamma emission from 100 MeV to 100 TeV (t0 = %.2e yr)'%t0[i]
        xlabel = 'Time [Myr]'
        ylabel = '$L_\gamma$ [erg s$^-1$]'
        figure_HESS = figure_number
        figure = figure_HESS + 1
        """
        for zone in (zones):

            if zone == 1:       # in the SB

                Lum_sb = interpolation1d(time, Lum_t_sb)


            elif zone == 2:     # in the supershell

                Lum_shell = interpolation1d(time, Lum_t_shell)


            else:               # outside the SB

                Lum_out = interpolation1d(time, Lum_t_out)


        Lum_tot = interpolation1d(time, Lum_t_tot)

        Flux_tot = interpolation2d(spectrum, time, Flux)

        Lum_pwn_tot = interpolation1d(time, Lum_pwn_t)
        Lum_psr_tot = interpolation1d(time, Lum_psr_t)

        Radius = interpolation1d(time, Rsb_t)
        Velocity = interpolation1d(time, Vsb_t)
        Mass_shell = interpolation1d(time, Ms_t)
        Density_shell = interpolation1d(time, ns_t)

        for l in (indt):

            for zone in (zones):

                if zone == 1:       # in the SB

                    Lumsb_sn[l] += Lum_sb(t[l])

                elif zone == 2:     # in the supershell

                    Lumshell_sn[l] += Lum_shell(t[l])

                else:               # outside the SB

                    Lumout_sn[l] += Lum_out(t[l])

            Lumtot_sn[l] += Lum_tot(t[l])

            Flux_sn[l] += Flux_tot(spectrum, t[l])
            Lum_pwn_sn[l] += Lum_pwn_tot(t[l])
            Lum_psr_sn[l] += Lum_psr_tot(t[l])

        R_sb = Radius(t)
        V_sb = Velocity(t)
        M_s = Mass_shell(t)
        n_s = Density_shell(t)

    return Lumtot_sn, Flux_sn, Lum_pwn_sn, Lum_psr_sn, nob, R_sb, V_sb, M_s, n_s

def energy_gamma(lum_gamma, time):

    """
    Return the energy radiation by gamma photons.

    Inputs:
        lum_gamma   :   intrinsic luminosity (erg s^-1)
        time        :   time array (yr)

    Output:
        E_gamma     :   total energy radiation (erg)
    """

    time = time * yr2s

    energy = integrate.trapz(lum_gamma, time)
    energy = numpy.nan_to_num(energy)

    return energy

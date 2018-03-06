"""
Here are all functions needed for the superbubble model
"""

##----------##
# Librairies #
##----------##
import matplotlib.pyplot as plt
import numpy
import scipy.integrate as integrate
from scipy.special import erf, erfc

##-----------------------------------------##
# Physical constants and Conversion factors #
##-----------------------------------------##
from Physical_constants import *
from Conversion_factors import *

##---------##
# Functions #
##---------##

def log_plot(figure_number, number_of_plot, x, y, label_name, title, xlabel, ylabel, symbol):
    """
    Function to plot a log-log graphic
    Inputs:
        figure_number:      define the number of the figure
        number_of_plot:     define how many plot do you want on one figure (with the same axis)
        x:                  x-vector
        y:                  y-array (line = one y-array and row = each different y-plot)
        label_name:         legend of one plots
        title:              title of the plot
        xlabel:             label of the x-axis
        ylabel:             label of the y-axis
    """
    plt.figure(figure_number)

    if number_of_plot > 1:

        for i in range (number_of_plot):
            y_plot = y[i]

            if len(symbol) > 1:
                sym = symbol[i]

            if label_name == 'none':
                plt.loglog(x, y_plot, symbol)

            else:
                plt.loglog(x, y_plot, sym, label = label_name[i])
                plt.legend(loc = 'best')

    elif label_name == 'none':
        plt.loglog(x, y, symbol)

    else:
        plt.loglog(x, y, symbol, label = label_name)
        plt.legend(loc = 'best')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    #plt.show()
    return

def plot(figure_number, number_of_plot, x, y, label_name, title, xlabel, ylabel, symbol):
    """
    Function to plot a linear graphic
    Inputs:
        figure_number:      define the number of the figure
        number_of_plot:     define how many plot do you want on one figure (with the same axis)
        x:                  x-vector
        y:                  y-array (line = one y-array and row = each different y-plot)
        label_name:         legend of one plots
        title:              title of the plot
        xlabel:             label of the x-axis
        ylabel:             label of the y-axis
    """
    plt.figure(figure_number)

    if number_of_plot > 1:

        for i in range (number_of_plot):
            y_plot = y[i,:]
            if label_name == 'none':
                plt.plot(x, y_plot, symbol[i])
            else:
                plt.plot(x, y_plot, symbol[i], label = label_name[i])
                plt.legend(loc = 'best')

    elif label_name == 'none':
        plt.plot(x, y, symbol)

    else:
        plt.plot(x, y, symbol, label = label_name)
        plt.legend(loc = 'best')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    return

def radius_velocity_SB(ar, alphar, betar, gammar, n0, L36, t6):
    """
    Function to compute the radius and the velocity of the forward shock of a superbubble
    From the equation 52 and 53 of the article Weaver et al. 1977
        Rsb = ar * n0^alphar * L36^betar * t6^gammar                    (pc)
        Vsb = dRsb/dt = ar * gammar * n0^alphar  L36^betar * t6^gammar  (km/s)
    Inputs:
        ar      :       numerical factor
        alphar  :       exponent of the density
        betar   :       exponent of the luminosity
        gammar  :       exponent of the time
        n0      :       atomic density expressed in cm^-3
        L36     :       total luminosity injected by the stars and SN expressed in 10^36 erg/s
        t6      :       age of the system expressed in 10^6 yr
    """

        # Outer radius of the SB (pc)
            # R_sb = ar * n0^alphar * L36^betar * t6^gammar
    Rsb = ar * n0**alphar * L36**betar * t6**gammar

        # Velocity of the forward shock
            # Vsb = dRsb/dt = gammar * ar * n0^alphar * L36^betar * t6^(gammar-1)
    Vsb = ar*(gammar) * n0**alphar * L36**betar * t6**(gammar-1)

    return Rsb, Vsb

def masses(an, alphan, betan, gamman, deltan, n0, L38, t7, Rsb, mu):
    """
    Function to compute the mass in the superbubble and the swept-up mass by the superbubble
    From the equation 5 of the article Mac Low and McCray (1987)
        x = r/Rsb where r is the distance to the center of the superbubble (pc) and Rsb is the outer radius (pc)
        n(x) = an * n0^alphan * L38^betan * t7^gamman * (1-x)^deltan        (cm^-3)
    Inputs:
        an      :       numerical factor
        alphan  :       exponent of the density
        betan   :       exponent of the luminosity
        gamman  :       exponent of the time
        deltan  :       exponent of the radius
        n0      :       atomic density expressed in cm^-3
        L38     :       total luminosity injected by the stars and the SNRs expressed in 10^38 erg/s
        t7      :       age of the system expressed in 10^8 yr
        Rsb     :       outer radius of the superbubble expressed in pc
        mu      :       average molecular weight
    """

        # mass within the superbubble (solar mass)
        # integral over x of the density in the SB
    integral_msb = integrate.quad(lambda x: (1-x)**deltan * x**2, 0, 1)[0]
    Msb = 4*numpy.pi * (Rsb*pc2cm)**3 * an * n0**alphan * L38**betan * t7**gamman * integral_msb * mu * mpg/Msun2g

        # swept-up mass (solar mass)
        # Mswept = Volume_sb * n0 * mu * mpg
    Mswept = 4*numpy.pi/3.0 * (Rsb*pc2cm)**3 * n0 * mu * mpg/Msun2g

    return Msb, Mswept

def density_thickness_shell(mu, n0, Vsb, C02, Mswept, Msb, Rsb):
    """
    Function to compute the density and the thickness of the shell
    From the equation 67 of the article Weaver et al. (1977)
        ns = n0 * (Vsb^2 + C0^2)/Cs^2
        where Cs^2 = kb*Ts/(mu*mpg)
    Inputs:
        mu      :       average molecular weight
        n0      :       atomic density (cm^-3)
        Vsb     :       velocity of the forward shock (km/s)
        C02     :       isothermal sound speed in the ambient medium (km/s)
        Mswept  :       swept-up mass by the suerbubble (solar masses)
        Msb     :       mass in the superbubble (solar masses)
        Rsb     :       outer radius of the superbubble (pc)
    """
        # density in the shell (cm^-3)
    Ts = 1e4                                    # temperature of the shell (K)
    Cs2 = kb*Ts/(mu*mpg)/(km2cm)**2             # isothermal sound speed in the shell (km/s)
    ns = n0 * (Vsb**2 + C02)/Cs2                # density in the shell (cm^-3)

        # thickness of the shell (pc)
    Ms = (Mswept-Msb)*Msun2g                                    # mass in the shell (g)
    Vs = Ms/(ns * mu * mpg)                                     # volume of the shell (cm^3)
    Rc = numpy.exp(numpy.log(Rsb**3 - 3/(4*numpy.pi)*Vs/(pc2cm**3))*1/3.0)  # radius of the continuity contact (pc)
    hs = Rsb-Rc                                                 # thickness of the shell (pc)

    return ns, hs

def pressure_SB(ap, alphap, betap, gammap, n0, L36, t6):
    """
    Function to compute the pressure in the superbubble
    From the equation 22 of the article Weaver et al. (1977)
        p = ap * n0^alphap * L36^betap * t6^gammap
    Inputs:
        ap      :       numerical factor
        alphap  :       exponent of the density
        betap   :       exponent of the luminosity
        gammap  :       exponent of the time
        n0      :       atomic density expressed in cm^-3
        L36     :       total luminosity injected by the stars and SN expressed in 10^36 erg/s
        t6      :       age of the system expressed in 10^6 yr
    """
    return ap * n0**(alphap) * L36**(betap) * t6**(gammap)

def luminosity_SB(al, etal, zeta, at, alphat, betat, gammat, deltat, an, alphan, betan, gamman, deltan, n0, L38, t7, epsilon, Rsb):
    """
    Function to compute the pressure in the superbubble
    From the equation 6 of the article Mac Low and McCray (1987)
        C = ne * n * LambdaT                :   cooling rate per unit volume (erg cm^-3 s^-1)
        where LambdaT = al * T6^etal * zeta (erg cm^3 s^-1)
              ne = epsilon * n              : density of electrons (cm^-3)
        Lsb = int_Volumesb (C)          (erg/s)
    Inputs:
        # expression of LambdaT = al * T6^etal * zeta
        al      :       numerical factor in the expression of LambdaT
        etal    :       exponent of the temperature in the expression of LambdaT
        zeta    :       metallicity of the local ISM (in the expression of LambdaT)
        # expression of T = at * n0^alphat * L38^betat * t7^deltat * (1-x)^deltat
        at      :       numerical factor in the expression of T
        alphat  :       exponent of the density in the expression of T
        betat   :       exponent of the luminosity in the expression of T
        gammat  :       exponent of the time in the expression of T
        deltat  :       exponent of the radius in the expression of T
        # expression of n = an * n0^alphan * L38^betan * t7^deltan * (1-x)^deltan
        an      :       numerical factor in the expression of n
        alphan  :       exponent of the density in the expression of n
        betan   :       exponent of the luminosity in the expression of n
        gamman  :       exponent of the time in the expression of n
        deltan  :       exponent of the radius in the expression of n
        # others parameters
        n0      :       atomic density expressed in cm^-3
        L38     :       total luminosity injected by the stars and SN expressed in 10^38 erg/s
        t7      :       age of the system expressed in 10^7 yr
        epsilon :       ratio ne/n
        Rsb     :       outer radius of the superbubble (pc)
    """
    at6 = at * K26K
    deltax = 2 * deltan + etal * deltat
    integral_lsb = integrate.quad(lambda x: (1-x)**deltax * x**2, 1, 0)[0]
    return al * zeta * (at6 * n0**alphat * L38**betat * t7**gammat)**(etal) * epsilon * (an * n0**alphan * L38**betan * t7**gamman)**2 * integral_lsb * (Rsb*pc2cm)**3 # in erg/s

def profile_density_temperature(at, alphat, betat, gammat, deltat, an, alphan, betan, gamman, deltan, n0, L38, t7, rsb, Rsb):
    """
    Function to compute the density and the temperature profiles in the superbubble
    From equations 4 and 5 of the article of Mac Low and McCray (1987)
        x = r/Rsb where r is the distance to the center of the SB (pc) and Rsb is the outer radius (pc)
        T(x) = at * n0^alphat * L38^betat * t7^gammat * (1-x)^deltat    (K)
        n(x) = an * n0^alphan * L38^betan * t7^gamman * (1-x)^deltan    (cm^-3)
    Inputs:
        # expression of T = at * n0^alphat * L38^betat * t7^deltat * (1-x)^deltat
        at      :       numerical factor in the expression of T
        alphat  :       exponent of the density in the expression of T
        betat   :       exponent of the luminosity in the expression of T
        gammat  :       exponent of the time in the expression of T
        deltat  :       exponent of the radius in the expression of T
        # expression of n = an * n0^alphan * L38^betan * t7^deltan * (1-x)^deltan
        an      :       numerical factor in the expression of n
        alphan  :       exponent of the density in the expression of n
        betan   :       exponent of the luminosity in the expression of n
        gamman  :       exponent of the time in the expression of n
        deltan  :       exponent of the radius in the expression of n
        # others parameters
        n0      :       atomic density expressed in cm^-3
        L38     :       total luminosity injected by the stars and SN expressed in 10^38 erg/s
        t7      :       age of the system expressed in 10^7 yr
        R_sb    :       array of distance (pc)
        Rsb     :       outer radius of the SB (pc)
    """
    x = rsb/Rsb
    Tsb = at * n0**alphat * L38**betat * t7**gammat * (1-x)**deltat
    nsb = an * n0**alphan * L38**betan * t7**gamman * (1-x)**deltan

    return Tsb, nsb

def power_law_distribution(Emin, Emax, E, alpha, eta, Esn, p0):
    """
    Function to compute the power-law distribution of the CR particles
    Inputs:
        Emin    :       minimum energy of the distribution (GeV)
        Emax    :       maximum energy of the distribution (GeV)
        E       :       energy array (GeV)
        alpha   :       exponent of the power-law distribution
        eta     :       efficiency of the cosmic rays acceleration
        Esn     :       energy released by the SN explosion (GeV)
        p0      :       normalization constant (GeV/c)
    """
    mpgev = mp*MeV2GeV  # mass of the proton in GeV

    integral_E = integrate.quad(lambda E: (E**2 + 2*mpgev*E)**(-(1 + alpha)/2.0) * (E + mpgev) * E, Emin, Emax)[0]
    N0 = eta * Esn * cl**(1-alpha) * p0**(-alpha) * 1.0/integral_E         # normalization constant (GeV^-1 c)

    return N0/cl**(1-alpha) * (E**2 + 2*mpgev*E)**(-(1+alpha)/2.0) * (E + mpgev)/p0**(-alpha)    # GeV^-1

def diffusion_coefficient(p0, D0, E, delta):
    """
    Function to compute the diffusion coefficient with a power-law
    Inputs:
        p0      :       normalization constant (GeV/c)
        D0      :       diffusion coefficient at p0 (cm^2 s^-1)
        E       :       energy array (GeV)
        delta   :       exponent of the power-law expression
    """
    mpgev = mp*MeV2GeV  # mass of the proton in GeV
    return D0 * (numpy.sqrt(E**2 + 2*mpgev*E)/p0)**delta

def diffusion_spherical(t, r, t0, NE, D):
    """
    Function to the density of the cosmic rays at each time and radius
        N(E, r, deltat) = N(E, 0, t0)/(4*pi*D(E)*deltat) * exp(-r^2/(4*D(E)*deltat))
    Inputs:
        t       :       time (yr)
        r       :       distance (pc)
        t0      :       time when the SN explode (yr) for the test if the SN has already exploded
        NE      :       initial density of the population of CR (GeV^-1)
        D       :       diffusion coefficient (cm^2 s^-1)
    """
    #rmin = 0                    # minimum radius (pc)
    #rmax = R_max                # maximum radius (pc)
    #number_bin_r = (rmax-rmin)/dr + 1
    #r = numpy.linspace(rmin, rmax, number_bin_r)    # position in pc

    delta_t = t - t0            # time after the SN explosion (yr)
    delta_t = delta_t * yr2s    # in s

        # density of the particles in time and position (GeV^-1)
    N = numpy.zeros(len(NE))

    if delta_t >= 0:            # if there is already an explosion
        if t == t0:        # at the SN explosion
            print(explosion)
            N = NE
        else:
            N = NE/((4*numpy.pi*D*(delta_t))**(3/2.0))*numpy.exp(-(r*pc2cm)**2/(4*D*(delta_t)))
    return N

def shell_particles(r_in, r_out, NE, D, t):
    """
    Function to compute the number of particles in a shell of inner radius r_in and outer radius r_out
    Inputs:
        r_in        :       inner radius of the shell (pc)
        r_out       :       outer radisu of the shell (pc)
        NE          :       initial particles distribution (GeV^-1)
        D           :       diffusion coefficient (cm^2 s^-1)
        t           :       time (yr)
    """

    r_out = r_out * pc2cm   # in cm
    r_in = r_in * pc2cm     # in cm
    t = t * yr2s            # in s

    a = r_in/(numpy.sqrt(4 * D * t))
    b = r_out/(numpy.sqrt(4 * D * t))

    #N = NE/(numpy.sqrt(numpy.pi)) * (numpy.sqrt(numpy.pi) * (erf(b) - erf(a)) + 2 * numpy.exp(-a**2) * a - 2 * numpy.exp(-b**2) * b)

    return NE/(numpy.sqrt(numpy.pi)) * (numpy.sqrt(numpy.pi) * (erf(b) - erf(a)) + 2 * numpy.exp(-a**2) * a - 2 * numpy.exp(-b**2) * b)

def inf_particles(Rsb, NE, D, t):
    """
    Function to compute the number of particles outside the superbubble.
    Inputs:
        Rsb         :       outer radius of the SB (pc)
        NE          :       initial particles distribution (GeV^-1)
        D           :       diffusion coefficient (cm^2 s^-1)
        t           :       time (yr)
    """

    a = (Rsb*pc2cm)/(numpy.sqrt(4 * D * t * yr2s))

    return NE/(numpy.sqrt(numpy.pi)) * (numpy.sqrt(numpy.pi) * erfc(a) + 2 * numpy.exp(-a**2) * a)

def gauss(x, A, Dt):
    """
    Function to fit a gaussian on the density profile as function of the radius.
    Input:
        r       :   vector radius (pc)
    Fit parameters:
        A       :   normalization of the gaussian (pc)
        Dt      :   factor related to the standard deviation (pc^2 s^-1 yr)
    """
    return A/((4.*numpy.pi*Dt * yr2s)**(3/2.0))*numpy.exp(-(x)**2/(4.*Dt * yr2s))

def profile_gas_density(at, alphat, betat, gammat, deltat, an, alphan, betan, gamman, deltan, n0, L38, t7, Rsb, mu, Vsb, C02, Mswept, Msb, r):
    """
    Function to compute the gas desnity profile along a distance r (pc)
    Inputs:
        # expression of T = at * n0^alphat * L38^betat * t7^deltat * (1-x)^deltat
        at      :       numerical factor in the expression of T
        alphat  :       exponent of the density in the expression of T
        betat   :       exponent of the luminosity in the expression of T
        gammat  :       exponent of the time in the expression of T
        deltat  :       exponent of the radius in the expression of T
        # expression of n = an * n0^alphan * L38^betan * t7^deltan * (1-x)^deltan
        an      :       numerical factor in the expression of n
        alphan  :       exponent of the density in the expression of n
        betan   :       exponent of the luminosity in the expression of n
        gamman  :       exponent of the time in the expression of n
        deltan  :       exponent of the radius in the expression of n
        # others parameters
        n0      :       atomic density expressed in cm^-3
        L38     :       total luminosity injected by the stars and SN expressed in 10^38 erg/s
        t7      :       age of the system expressed in 10^7 yr
        Rsb     :       outer radius of the SB (pc)
        mu      :       average molecular weight
        Vsb     :       velocity of the forward shock (km/s)
        C02     :       isothermal sound speed in the ambient medium (km/s)
        Mswept  :       swept-up mass by the suerbubble (solar masses)
        Msb     :       mass in the superbubble (solar masses)
    """
    n = len(r) - 1
    dr = r[n]-r[n-1]
    nsb = profile_density_temperature(at, alphat, betat, gammat, deltat, an, alphan, betan, gamman, deltan, n0, L38, t7, Rsb, dr)[1]
    ns, hs = density_thickness_shell(mu, n0, Vsb, C02, Mswept, Msb, Rsb)

    n_tot = n0 * numpy.ones(n + 1)

    ind1 = numpy.where(r[1:] < Rsb-hs)[0]
    if len(nsb) > 0:

        n_tot[ind1] = nsb[ind1]

        ind2 = numpy.where((r >= Rsb-hs) & (r <= Rsb))[0]
        n_tot[ind2] = ns

    return n_tot

def integration_log(x, y):

    """
    Return the integrale of a function in log-log scale

    Parameters :
        x           : abscisse of the function
        y           : function that we integrate along x : y = f(x)
    """

    #Looking for a and b for y = a*x^b
    def calculate_ab(xi, xf, yi, yf):
        logxi = numpy.log(xi)
        logxf = numpy.log(xf)
        logyi = numpy.log(yi)
        logyf = numpy.log(yf)
        b = (logyf - logyi)/(logxf - logxi)
        loga = logyi - b*logxi
        a = numpy.exp(loga)
        a = numpy.nan_to_num(a)
        return a, b

    #Calculate deltaS from deltaS = int from xi to xf a*x^b
    def delta_S(xi, xf, yi, yf):
        [a, b] = calculate_ab(xi, xf, yi, yf)
        return a/(b+1)*(xf**(b+1) - xi**(b+1))

    integral = 0

    # Because the function integral_log works only if there is more than two elements not zero
    idx=(y > 0.0)
    #idy=(y < 0.0) # only used if the function has negative value
    idt = idx #+ idy
    if sum(idt) > 2:

        x = x[idt]
        y = y[idt]

        #Calculate total integral from init to final a*x^b
        deltaS = 0

        for i in range (1, len(x)):
            deltaS = delta_S(x[i-1], x[i], y[i-1], y[i])
            integral = integral + deltaS

            integral = numpy.nan_to_num(integral)

    return integral

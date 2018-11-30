'''where you can set absolute and relative path used in the package'''

import os

dir = os.path.dirname(os.path.abspath(__file__))

M2015_file = './data/aux/rhoTable_Mobley2015.csv'
M1999_file = './data/aux/rhoTable_Mobley1999.csv'
rhosoaa_fine_file = './data/aux/surface_reflectance_factor_rho_fine_aerosol_rg0.06_sig0.46.csv'
rhosoaa_coarse_file = './data/aux/surface_reflectance_factor_rho_coarse_aerosol_rg0.60_sig0.60.csv'

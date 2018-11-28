import os
import pandas as pd

dir = os.path.dirname(os.path.abspath(__file__))

#load Mobley tabulated values
rho_m1999 = pd.read_csv(os.path.join(dir,'data/aux/rhoTable_Mobley1999.csv'), skiprows=7)
rho_m2015 = pd.read_csv(os.path.join(dir,'data/aux/rhoTable_Mobley2015.csv'), skiprows=8)
import os
import numpy as np

from rho_factor.gen_rho import generate_rho_values as g

gg = g.generate()

gg.azi = np.linspace(0, 180, 13)
gg.sza = np.linspace(0, 80, 21)
gg.vza = np.linspace(0, 80, 17)

gg.execute()

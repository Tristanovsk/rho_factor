from rho_factor.config import *
from rho_factor.gen_rho.utils import *
from rho_factor.gen_rho.lut import *


class generate:
    '''
    variables:
        odir: output directory in which rho files are saved
        plot: plot rho values if True
        dir
        dirfig

        dirlut

        aero_fine_file: path of the netcdf lut file to be used for generating the rho values for the fine mode aerosols
        aero_coarse_file: path of the netcdf lut file to be used for generating the rho values for the coarse mode aerosols
        rho factor is enerated for the geometry parameters (array or numpy array):
        azi: relative azimuth (in deg), = 0 when looking at Sun
        vza: viewing zenith angle (in deg), =0 when looking at nadir, =90° when looking at horizon
        sza: solar zenith angles (in deg)
    '''

    def __init__(self, odir=os.path.abspath('./rho_values/')):
        self.plot = False
        self.dir = dir
        self.odir = odir
        self.dirfig = os.path.join(self.dir, 'fig')

        self.dirlut = os.path.join(self.dir, 'data/lut')

        self.aero_fine_file = os.path.join(self.dirlut,
                                           'lut_aeronet_osoaa_band_integrated_aot0.01_aero_rg0.06_sig0.46_ws0_pressure1015.2.nc')
        self.aero_coarse_file = os.path.join(self.dirlut,
                                             'lut_aeronet_osoaa_band_integrated_aot0.01_aero_rg0.60_sig0.60_ws0_pressure1015.2.nc')

        self.ofile_fine = os.path.join(self.odir, 'surface_reflectance_factor_rho_fine_aerosol_rg0.06_sig0.46.csv')
        self.ofile_coarse = os.path.join(self.odir, 'surface_reflectance_factor_rho_coarse_aerosol_rg0.60_sig0.60.csv')
        self.azi = np.linspace(0, 180, 13)
        self.vza = np.array([30, 40, 50])
        self.sza = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80])

    def execute(self):
        '''

        '''

        # -------------------------
        # rho for fine aerosol model
        lutf = lut(self.aero_fine_file, ws=[0, 2, 5, 10])
        lutf.generate_vza_compliant(vza=self.vza)
        # lutf.load_lut(vza_lim=[29, 51])
        rho = lutf.Lsurf / lutf.Lsky
        rho_g = (lutf.Lg + lutf.Lsurf) / lutf.Lsky
        arr = np.column_stack(list(map(np.ravel, np.meshgrid(*lutf.grid_lut))) + [rho.ravel()] + [rho_g.ravel()])
        df = pd.DataFrame(arr, columns=['wind', 'aot', 'wl', 'sza', 'azi', 'vza', 'rho', 'rho_g'])

        df_ = df[df.sza.isin(self.sza) & (df.azi.isin(self.azi))]
        df_.to_csv(self.ofile_fine, index=False)

        # -------------------------
        # rho for coarse aerosol model
        lutc = lut(self.aero_coarse_file, ws=[0, 2, 5, 10])
        lutc.generate_vza_compliant(vza=self.vza)
        # lutc.load_lut(vza_lim=[29, 51])
        rho = lutc.Lsurf / lutc.Lsky
        rho_g = (lutc.Lg + lutc.Lsurf) / lutc.Lsky
        arr = np.column_stack(list(map(np.ravel, np.meshgrid(*lutc.grid_lut))) + [rho.ravel()] + [rho_g.ravel()])
        df = pd.DataFrame(arr, columns=['wind', 'aot', 'wl', 'sza', 'azi', 'vza', 'rho', 'rho_g'])

        df_ = df[df.sza.isin(self.sza) & (df.azi.isin(self.azi))]
        df_.to_csv(self.ofile_coarse, index=False)

        if self.plot:
            figure().plot_lut_vs_wind(lutf, fout=os.path.join(self.dirfig, 'lut_fig'))

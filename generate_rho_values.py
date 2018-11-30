from config import *
from utils import *
from lut import *
import seaborn as sns

class generate:
    def __init__(self):
        pass

    def execute(self):
        dirfig = os.path.join(dir, 'fig')

        dirlut = os.path.join(dir, 'data/lut')

        aero_fine_file = os.path.join(dirlut,
                                      'lut_aeronet_osoaa_band_integrated_aot0.01_aero_rg0.06_sig0.46_ws0_pressure1015.2.nc')
        aero_coarse_file = os.path.join(dirlut,
                                        'lut_aeronet_osoaa_band_integrated_aot0.01_aero_rg0.60_sig0.60_ws0_pressure1015.2.nc')

        azi = np.linspace(0, 180, 13)
        vza = np.array([30, 40, 50])
        sza = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80])

        # -------------------------
        # rho for fine aerosol model
        lutf = lut(aero_fine_file, ws=[0, 2, 5, 10])
        lutf.generate_vza_compliant(vza=vza)
        # lutf.load_lut(vza_lim=[29, 51])
        rho = lutf.Lsurf / lutf.Lsky
        rho_g = (lutf.Lg + lutf.Lsurf) / lutf.Lsky
        arr = np.column_stack(list(map(np.ravel, np.meshgrid(*lutf.grid_lut))) + [rho.ravel()] + [rho_g.ravel()])
        df = pd.DataFrame(arr, columns=['wind', 'aot', 'wl', 'sza', 'azi', 'vza', 'rho', 'rho_g'])

        df_ = df[df.sza.isin(sza) & (df.azi.isin(azi))]
        df_.to_csv('./rho_values/surface_reflectance_factor_rho_fine_aerosol_rg0.06_sig0.46.csv', index=False)

        # -------------------------
        # rho for coarse aerosol model
        lutc = lut(aero_coarse_file, ws=[0, 2, 5, 10])
        lutc.generate_vza_compliant(vza=vza)
        # lutc.load_lut(vza_lim=[29, 51])
        rho = lutc.Lsurf / lutc.Lsky
        rho_g = (lutc.Lg + lutc.Lsurf) / lutc.Lsky
        arr = np.column_stack(list(map(np.ravel, np.meshgrid(*lutc.grid_lut))) + [rho.ravel()] + [rho_g.ravel()])
        df = pd.DataFrame(arr, columns=['wind', 'aot', 'wl', 'sza', 'azi', 'vza', 'rho', 'rho_g'])

        df_ = df[df.sza.isin(sza) & (df.azi.isin(azi))]
        df_.to_csv('./rho_values/surface_reflectance_factor_rho_coarse_aerosol_rg0.60_sig0.60.csv', index=False)

        g = sns.FacetGrid(df_[(df_.aot == 0.5)], col="sza", hue="wind", col_wrap=3, size=1.5, legend_out=True)
        g.map(plt.plot, "wl", "rho", marker="o", ms=4)
        g.add_legend()
        # g.set(xticks=np.arange(5), yticks=[-3, 3],xlim=(-.5, 4.5), ylim=(-3.5, 3.5))
        g.fig.tight_layout(w_pad=1)

        figure().plot_lut_vs_wind(lutf, fout=os.path.join(dirfig, 'lut_fig'))

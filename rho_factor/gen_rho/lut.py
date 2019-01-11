import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt

class lut:
    def __init__(self, file, aot=[0.0001, 0.01, 0.05, 0.1, 0.3, 0.5, 1.0], ws=[0, 2, 5, 10]):
        '''

        :param file:
        :param aot: array of scalar, aerosol optical thickness at the reference wavelength (i.e., 550 nm)
        :param ws: array of scalar, wind speed used for sea roughness (Cox-Munk model),
        '''
        self.lut_generator = "OSOAA_LOV"
        self.file = file
        self.wl = []
        self.Cext = []
        self.Cext_ref = 1
        self.aot = aot
        self.ws = ws
        self.Lg = []
        self.Lsurf = []
        self.Lsky = []

    def generate_vza_compliant(self, vza= (np.array([30,40,50]))):
        '''
        Load lut and interpolate values for a restricted range of angles given by angle_grid

        :param angle_grid: series of (sza, azi, vza) corresponding to the desired range of angle given in deg; by default: azi and vza of aeronet-oc are used
        :return:

        '''
        from scipy.interpolate import interp1d

        self.load_lut(vza_lim=[vza.min()-2,vza.max()+2],)
        Naot = len(self.aot)
        Nws = len(self.ws)

        self.vza = vza

        # allocate lut array
        dim = (Nws, Naot, len(self.wl), len(self.sza),len(self.azi),len(self.vza))
        Lg = np.ndarray(dim)
        Lsurf = np.ndarray(dim)
        Lsky = np.ndarray(dim)
        vza_grid = np.tile(vza, (  len(self.sza),len(self.azi), 1))
        #Lg = interp1d(self.grid_lut[-1], self.Lg)(vza_grid)
        for iws in range(Nws):
            for iaot in range(Naot):
                print(iws,iaot,self.grid_lut[-1],vza)
                for iwl in range(len(self.wl)):
                    Lg[iws, iaot,iwl,] = interp1d(self.grid_lut[-1], self.Lg[iws, iaot,iwl])(vza)
                    Lsurf[iws, iaot,iwl,] = interp1d(self.grid_lut[-1], self.Lsurf[iws, iaot,iwl])(vza)
                    Lsky[iws, iaot,iwl,] = interp1d(self.grid_lut[-1], self.Lsky[iws, iaot,iwl])(vza)

        self.Lg = Lg
        self.Lsurf = Lsurf
        self.Lsky = Lsky
        # update grid for interpolation
        self.grid_lut = (self.ws, self.aot, self.wl, self.sza, self.azi, self.vza)

    def load_lut(self, vza_lim=[0, 90],azi_lim=[0,180]):
        '''load lut calculated from OSOAA code
           dims: [wl, sza, azi, vza]

        :param vza_lim: array of min/max values for the desired vza range
        :param radiance: if True scale normalized radiance withh solar flux
        :return: load lut values in self object

        '''
        print('loading lut... please wait.')
        Nws = len(self.ws)
        Naot = len(self.aot)
        ok = 0
        for iws in range(Nws):
            for iaot in range(Naot):

                file = self.file.replace('aot0.01', 'aot' + str(self.aot[iaot])).replace('ws0',
                                                                                         'ws' + str(self.ws[iws]))
                #print 'loading ' + file
                lut = Dataset(file, mode='r')
                if ok == 0:
                    ok = 1
                    self.Cext = lut.variables['Cext'][:]
                    self.Cext_ref = lut.variables['Cext550'][:]
                    self.vza = lut.variables['vza'][:]
                    self.sza = lut.variables['sza'][:]
                    self.azi = lut.variables['azi'][:]
                    self.wl = lut.variables['wl'][:] * 1e3  # output in nm

                    # shrink azi and vza range
                    ind_vza = (self.vza >= vza_lim[0]) & (self.vza <= vza_lim[1])
                    self.vza = self.vza[ind_vza]
                    ind_azi = (self.azi >= azi_lim[0]) & (self.azi <= azi_lim[1])
                    self.azi = self.azi[ind_azi]
                    self.grid_lut = (self.ws,self.aot,self.wl,self.sza, self.azi, self.vza)

                    # allocate lut array
                    dim = (Nws, Naot, len(self.wl), len(self.sza), len(self.azi), len(self.vza))
                    self.Lg = np.ndarray(dim)
                    self.Lsurf = np.ndarray(dim)
                    self.Lsky = np.ndarray(dim)

                # fill in lut array
                self.Lg[iws, iaot, :, :, :, :] = lut.variables['Isunglint'][:, :, ind_azi, ind_vza]
                self.Lsurf[iws, iaot, :, :, :, :] = lut.variables['Isurf'][:, :, ind_azi, ind_vza]
                self.Lsky[iws, iaot, :, :, :, :] = lut.variables['Isky'][:, :, ind_azi, ind_vza]

        return

    def interpn_lut(self, points, values, x):
        '''expected x dims: [[sza1, azi1, vza1],[sza2, azi2, vza2]...]'''
        from scipy.interpolate import interpn
        interp = np.ma.masked_invalid(interpn(points, values, x))
        return interp

    def spline_lut(self, gin, lut, gout):
        '''
        Interpolation with two successive bicubic splines on a regular 4D grid.
        Designed for interpolation in radiative transfer look-up tables with the two last dimensions
        (i.e., wavelength and solar zenith angle) of the same length.
        Those dimensions are then reduced/merged to a single one to get interpolated data on a 3D grid.

        :param gin: regular 4D grid of the tabulated data (tuple/array/list of arrays)
        :param lut: tabulated data
        :param gout: new 4D grid on which data are interpolated (with dims 2 and 3 of the same length);
                    (tuple/array/list of arrays)
        :return: Interpolated data (1D or 3D array depending on the dimension shapes of gout
        '''
        import scipy.interpolate as si

        N = gin[0].__len__(), gin[1].__len__(), gin[2].__len__(), gin[3].__len__()
        Nout = gout[0].__len__(), gout[1].__len__(), gout[2].__len__()
        tmp = np.zeros([N[0], N[1], Nout[2]])

        for i in range(N[0]):
            for j in range(N[1]):
                tmp[i, j, :] = si.RectBivariateSpline(gin[2], gin[3], lut[i, j, :, :])(gout[2], gout[3], grid=False)
        if Nout[0]==Nout[1]==1:
            interp = np.ndarray(Nout[2])
            for iband in range(Nout[2]):
                interp[iband] = si.RectBivariateSpline(gin[0], gin[1], tmp[:, :, iband])(gout[0], gout[1], grid=False)
        else:
            interp = np.ndarray([Nout[0], Nout[1], Nout[2]])
            for iband in range(Nout[2]):
                interp[:, :, iband] = si.RectBivariateSpline(gin[0], gin[1], tmp[:, :, iband])(gout[0], gout[1], grid=True)

        return interp

    def plot_lut(self, vza, azi, values):
        '''
        Plot polar diagram (vza, azi) of the given LUT

        :param vza:
        :param azi:
        :param values:
        :return:
        '''
        from scipy.interpolate import RectBivariateSpline

        spl = RectBivariateSpline(azi, vza, values)

        azi_ = np.linspace(0, max(azi), 360)
        vza_ = np.linspace(0, max(vza), 150)
        values_ = spl(azi_, vza_, grid=True)

        r, theta = np.meshgrid(vza_, np.radians(azi_))
        fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
        # ax.contourf(theta,r, values)
        quadmesh = ax.pcolormesh(theta, r, values_)
        ax.grid(True)
        fig.colorbar(quadmesh, ax=ax)

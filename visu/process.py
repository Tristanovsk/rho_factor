import numpy as np
import pandas as pd
import scipy.interpolate as si
import plotly.plotly as py
# import plotly.graph_objs as go
from plotly.graph_objs import *


class rho:
    def __init__(self, df=None, wl=None, rho_file=None):
        self.df = df
        self.aot = 0.1
        self.ws = 2
        self.wl = wl
        if rho_file == None:
            # TODO put rho_file in a config.py file
            rho_file = "/DATA/git/rho_factor/rho_values/surface_reflectance_factor_rho_fine_aerosol_rg0.06_sig0.46.csv"
        self.rho_file = rho_file
        self.load_rho_lut()

    def load_rho_lut(self):
        self.rho = pd.read_csv(self.rho_file, index_col=[0, 1, 2, 3, 4, 5])

    def get_rho_values(self, ws=2, aot=0.1, sza=[30], wl=None):

        if all(wl != None):
            self.wl = wl

        grid = self.rho.rho.index.levels
        # convert pandas dataframe into 6D array of the tabulated rho values for interpolation
        rho_ = reshape().df2ndarray(self.rho, 'rho')

        rho_wl = calc().spline_4d(grid, rho_[:, :, :, :, 1, 1], ([ws], [aot], self.wl, sza))
        return rho_wl

    def process(self, ws=2, aot=0.1):

        wl = self.wl
        df = self.df
        rho = self.get_rho_values(wl=wl, sza=df['sza'].values.mean())
        self.Rrs = (df.loc[:, ("Lt")] - rho * df.loc[:, ("Lsky")]) / df.loc[:, ("Ed")]
        self.Rrs.columns = pd.MultiIndex.from_product([['Rrs(awr)'], self.Rrs.columns], names=['param', 'wl'])

        return self.Rrs, rho


class calc:
    def __init__(self):
        pass

    def earth_sun_correction(self, dayofyear):
        '''
        Earth-Sun distance correction factor for adjustment of mean solar irradiance

        :param dayofyear:
        :return: correction factor
        '''
        theta = 2. * np.pi * dayofyear / 365
        d2 = 1.00011 + 0.034221 * np.cos(theta) + 0.00128 * np.sin(theta) + \
             0.000719 * np.cos(2 * theta) + 0.000077 * np.sin(2 * theta)
        return d2

    def bidir(self, sza, vza, azi):

        bidir = 1

        return bidir

    def spline_4d(self, gin, lut, gout):
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
        if Nout[0] == Nout[1] == 1:
            interp = np.ndarray(Nout[2])
            for iband in range(Nout[2]):
                interp[iband] = si.RectBivariateSpline(gin[0], gin[1], tmp[:, :, iband])(gout[0], gout[1], grid=False)
        else:
            interp = np.ndarray([Nout[0], Nout[1], Nout[2]])
            for iband in range(Nout[2]):
                interp[:, :, iband] = si.RectBivariateSpline(gin[0], gin[1], tmp[:, :, iband])(gout[0], gout[1],
                                                                                               grid=True)

        return interp


class reshape:
    def __init__(self):
        pass

    def ndarray2df(self, arr, grid, names):
        arr = np.column_stack(list(map(np.ravel, np.meshgrid(*grid))) + [arr.ravel()])
        df = pd.DataFrame(arr, columns=names)  # e.g., names=['wind','aot','wl','sza','azi','vza','rho','rho_g'])
        return df

    def df2ndarray(self, df, name):
        shape = map(len, df.index.levels)
        arr = np.full(shape, np.nan)
        # fill it using Numpy's advanced indexing
        arr[df.index.labels] = df[name].values.flat
        return arr

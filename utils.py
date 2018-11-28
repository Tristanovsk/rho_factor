import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages as pdf
import datetime
import math
import numpy as np
import pandas as pd
import scipy.interpolate as si

class calc:
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


class figure:

    def __init__(self):
        pass

    def compar_band_multipage(self, df, fout, xname='Li_Mean_val', yname='Lsky', cname='Solar_Zenith', title=''):
        plt.ioff()
        with pdf(fout) as p:
            for (wl, group) in df.groupby(level=2, axis=1):
                if wl != '':
                    print wl
                    group.dropna(inplace=True)
                    x = group.xs(xname, level=1, axis=1).values[:, 0]
                    y = group.xs(yname, level=1, axis=1).values[:, 0]
                    c = group.xs(cname, level=1, axis=1).values[:, 0]

                    fig, self.ax = plt.subplots(figsize=(6, 6))
                    ymax = max(x.max(), y.max())
                    self.ax.set(xlim=(0, ymax), ylim=(0, ymax), aspect=1)
                    self.ax.plot([0, ymax], [0, ymax], '--', color='grey')
                    im = self.ax.scatter(x, y, c=c, cmap='gnuplot')
                    self.annot(x, y, ymax)
                    fig.colorbar(im, ax=self.ax)
                    fig.suptitle(title + ' at ' + str(wl) + ' nm')
                    fig.tight_layout()

                    p.savefig()
                    fig.close()

            d = p.infodict()
            d['Title'] = 'Simulations vs measurements comparison '
            d['Author'] = u'T. Harmel (SOLVO)'
            d['CreationDate'] = datetime.datetime.today()

    def compar_band_subplots(self, df, fout, xname='Li_Mean_val', yname='Lsky', cname='Solar_Zenith', title='',
                             format='png'):
        '''
        Function used to generate comparison figures of standard vs solvo parameters

        :param df: data frame containing data to plot
        :param fout: path name under which figure is saved
        :param xname: x-axis parameter
        :param yname: y-axis parameter
        :param cname: parameter to be used as color scale
        :param title: title appearing at the top of the figure
        :param format: output format of the figure, can be either 'pdf' or 'png' (default)
        :return:
        '''

        plt.ioff()
        grouped = df.groupby(level=2, axis=1)
        group_scalar = grouped.get_group('')
        nrow = int(math.ceil((len(grouped) - 1) / 4.))  # "-1" because of one extra group without wavelength

        #with pdf(fout) as p:
        fig, axs = plt.subplots(nrow, 4, figsize=(16, 9))
        for (wl, group), self.ax in zip(grouped, axs.flatten()):
            if wl != '':
                # print wl
                group.dropna(inplace=True)
                x = group.xs(xname, level=1, axis=1).values[:, 0]
                y = group.xs(yname, level=1, axis=1).values[:, 0]
                if cname in group_scalar.columns.get_level_values(1):
                    group = pd.merge(group, group_scalar, how='inner', left_index=True, right_index=True)

                c = group.xs(cname, level=1, axis=1).values[:, 0]

                ymax = max(x.max(), y.max())
                self.ax.set(xlim=(0, ymax), ylim=(0, ymax), aspect=1, title=str(wl) + ' nm')
                self.ax.set(xlabel=xname, ylabel=yname)
                self.ax.plot([0, ymax], [0, ymax], '--', color='grey')
                self.ax.scatter(x, y, c=c, cmap='gnuplot')
                self.annot(x, y, ymax)
        # fig.tight_layout()
        fig.subplots_adjust(right=0.9)
        cbar_ax = fig.add_axes([0.94, 0.2, 0.025, 0.6])
        fig.colorbar(axs[0][0].get_children()[0], cax=cbar_ax, label=cname)
        fig.suptitle(title)
        fig.tight_layout(rect=[0.025, 0.025, 0.93, 0.95])

        if format == 'pdf':
            # p.savefig()
            #
            # d = p.infodict()
            # d['Title'] = 'Simulations vs measurements comparison '
            # d['Author'] = u'T. Harmel (SOLVO)'
            # d['CreationDate'] = datetime.datetime.today()
            fig.savefig(os.path.splitext(fout)[0]+'.pdf')
        else:
            fig.savefig(os.path.splitext(fout)[0]+'.png')

    def multipage_compar(self, df, fout, title=''):
        plt.ioff()
        with pdf(fout) as p:
            for (wl, group) in df.groupby(df.wl):
                fig, self.ax = plt.subplots(figsize=(6, 6))
                ymax = max(group.Lsky_mes.max(), group.Lsky_sim.max())
                self.ax.set(xlim=(0, ymax), ylim=(0, ymax), aspect=1)
                self.ax.plot([0, ymax], [0, ymax], '--', color='grey')
                self.annot(group.Lsky_mes, group.Lsky_sim, ymax)

                group.plot(x='Lsky_mes', y='Lsky_sim', c="sza", kind='scatter', cmap='gnuplot', ax=self.ax,
                           title=title + ' at ' + str(wl) + ' nm')
                p.savefig()
                plt.close()
            d = p.infodict()
            d['Title'] = 'Simulations vs measurements comparison '
            d['Author'] = u'T. Harmel (SOLVO)'
            d['CreationDate'] = datetime.datetime.today()

    def subplots_compar(self, df, fout, title=''):

        Nwl = len(df.wl.unique())
        Nplot = int(math.ceil(Nwl ** 0.5))
        fig, axes = plt.subplots(Nplot, Nplot, figsize=(20, isza))
        fig.suptitle(title)

        for ax in axes.flatten():
            ax.set_visible(False)
        for (wl, group), ax in zip(df.groupby(df.wl), axes.flatten()[0:Nwl]):
            ax.set_visible(True)
            ymax = max(group.Lsky_mes.max(), group.Lsky_sim.max())
            ax.set(xlim=(0, ymax), ylim=(0, ymax), aspect=1)
            ax.plot([0, ymax], [0, ymax], '--', color='grey')
            group.plot(x='Lsky_mes', y='Lsky_sim', c="sza", kind='scatter', cmap='gnuplot', ax=ax, title=wl,
                       colorbar=False)

        fig.tight_layout()
        fig.subplots_adjust(right=0.92)
        cbar_ax = fig.add_axes([0.92, 0.2, 0.025, 0.6])
        fig.colorbar(axes[0][0].get_children()[0], cax=cbar_ax, label='Solar Zenith Angle (deg)')

        fig.savefig(fout)

        # df.plot.scatter(x='Lsky_mes', y='Lsky_sim', c='wl', s=50, cmap="rainbow")
        # plt.figure()
        # plt.plot(wl, Lsky_f)
        # plt.plot(wl, Lsky_c)
        # plt.plot(wl, Lsky)
        # plt.plot(wl, Lsky_a)

    def linearfit(self, x, y):
        '''
        Linear regression between y and x

        :param x: x parameter
        :param y: y parameter
        :return: slope, intercept, r_value, p_value, std_err
        '''
        from scipy import stats

        return stats.linregress(x, y)

    def stats(self, x, y):
        '''
        Compute statistical indicators between x and y parameters

        :param x: x parameter
        :param y: y parameter
        :return:
            * N: number of points
            * r2: coefficient of determination
            * rmse: root mean square error
            * mae: mean absolute error
            * slope and intercept of the regression line
        '''
        import sklearn.metrics as sk

        slope, intercept, r, p, std = self.linearfit(x, y)
        N = len(x)
        rmse = sk.mean_squared_error(x, y)
        nrmse = rmse / np.nanmean(x)
        mae = sk.mean_absolute_error(x, y)
        r2 = r ** 2  # sk.r2_score(x,y)

        return N, r2, rmse, nrmse, mae, slope, intercept

    def annot(self, x, y, ymax, fontsize=11):
        '''
        Generate figure legend with statistical indicators

        :param x: x parameter
        :param y: y parameter
        :param ymax: maximum value of the dataset used to scale axis
        :param fontsize: font size of legend
        :return:
        '''

        N, r2, rmse, nrmse, mae, slope, intercept = self.stats(x, y)
        xx = np.append(x, [0., ymax])
        self.ax.plot(xx, slope * xx + intercept, 'k', lw=2)

        text = r'y=${0:.3f}x+${1:.3f}'.format(slope, intercept) + '\n' + r'R$^2=${0:.4f}'.format(
            r2) + '\n' + r'N={0}'.format(N)
        self.ax.text(ymax * 0.025, ymax * 0.8, text, fontsize=fontsize)

        text = r'mse={0:.3f}'.format(rmse) + '\n' + r'nmse={0:.2f}%'.format(nrmse * 100)
        self.ax.text(ymax * 0.6, ymax * 0.05, text, ha='left', fontsize=fontsize)

    def set_axlims(self, series, marginfactor=0.05):
        """
        Fix for a scaling issue with matplotlibs scatterplot and small values.
        Takes in a pandas series, and a marginfactor (float).
        A marginfactor of 0.2 would for example set a 20% border distance on both sides.
        Output:[bottom,top]
        To be used with .set_ylim(bottom,top)
        """
        minv = series.min()
        maxv = series.max()
        datarange = maxv - minv
        border = abs(datarange * marginfactor)
        maxlim = maxv + border
        minlim = minv - border

        return minlim, maxlim

    def plot_lut_vs_wind(self, lut_, fout='', iaot=0, iwl=4):

        idx = 0

        g = lut_.grid_lut
        # lutdata = lut_.Lsurf
        # for iws in range(g[0].__len__()):
        #     for iaot in range(g[1].__len__()):
        #         si.interpn((g[2],g[3]),lutdata[iws,iaot,:,:], (wls,szas),method='splinef2d')

        xx = np.linspace(np.min(lut_.grid_lut[idx]), np.max(lut_.grid_lut[idx]), 50)
        newgrid = (xx, 0.1)
        isza = [5, 15, 30]
        wls = np.repeat(g[2][iwl], isza.__len__())
        gout = [xx, [g[1][iaot]], wls, g[3][isza]]
        Lsurf = lut_.spline_lut(g, lut_.Lsurf, gout)
        Lsky = lut_.spline_lut(g, lut_.Lsky, gout)
        Lg = lut_.spline_lut(g, lut_.Lg, gout)
        Lg[Lg < 0] = 0

        # fig, axes = plt.subplots(2,2, figsize=(10, 7))
        # for iband in range(len(gout[2])):
        #     sza = gout[3][iband]
        #     axes[0,0].scatter(g[0],lut_.Lsurf[:,iaot,iwl,isza[iband]])
        #     axes[0,0].plot(xx,Lsurf[:,0,iband], label=sza)
        #     axes[0,1].scatter(g[0],lut_.Lsky[:,0,iwl,isza[iband]])
        #     axes[0,1].plot(xx,Lsky[:,0,iband], label=sza)
        #     axes[1,0].scatter(g[0],lut_.Lg[:,0,iwl,isza[iband]])
        #     axes[1,0].plot(xx,Lg[:,0,iband], label=sza,linestyle=':')
        #     axes[1,1].scatter(g[0],lut_.Lsurf[:,0,iwl,isza[iband]]/lut_.Lsky[:,0,iwl,isza[iband]])
        #     color = next(axes[1,1]._get_lines.prop_cycler)['color']
        #     yy = Lsurf[:,0,iband] / Lsky[:,0,iband]
        #     axes[1,1].plot(xx,yy,color=color, label=sza)
        #     axes[1,1].scatter(g[0],(lut_.Lsurf[:,0,iwl,isza[iband]]+lut_.Lg[:,0,iwl,isza[iband]])/lut_.Lsky[:,0,iwl,isza[iband]], color=color)
        #     yy = (Lsurf[:,0,iband] + Lg[:,0,iband]) / Lsky[:,0,iband]
        #     axes[1,1].plot(xx,yy,linestyle=':', color=color)
        #
        # axes[1,1].legend(title=r'$\theta_s$ (deg)')
        # axes[0,0].set(ylabel=r'$L_{surf}$',ylim=self.set_axlims(lut_.Lsurf[:,iaot,iwl,:]))
        # axes[0,1].set(ylabel=r'$L_{sky}$')
        # axes[1,0].set(xlabel=r'Wind speed (m $s^{-1}$)',ylabel=r'$L_g$',ylim=self.set_axlims(lut_.Lg[:,iaot,iwl,:]))
        # axes[1,1].set(xlabel=r'Wind speed (m $s^{-1}$)',ylabel=r'rho')
        # fig.suptitle('wl: '+str(g[2][iwl])+'nm; AOT: '+str(g[1][iaot]))
        #
        # fig.tight_layout(rect=[0, 0., 1, 0.95])

        fig, axes = plt.subplots(2, 2, figsize=(10, 7))
        for isza in [5, 15, 30]:
            sza = g[3][isza]
            Lsurf = si.RectBivariateSpline(g[0], g[1], lut_.Lsurf[:, :, iwl, isza], kx=3)(xx, g[1][
                iaot])  # si.interpn((g[0],g[1]),lut_.Lsurf[:,:,3,isza], newgrid,method='splinef2d')
            Lsky = si.RectBivariateSpline(g[0], g[1], lut_.Lsky[:, :, iwl, isza], kx=3)(xx, g[1][
                iaot])  # lut_.interp_lut(lut_.grid_lut,lut_.Lsky, newgrid)
            Lg = si.RectBivariateSpline(g[0], g[1], lut_.Lg[:, :, iwl, isza], kx=3)(xx, g[1][
                iaot])  # lut_.interp_lut(lut_.grid_lut,lut_.Lg, newgrid)
            Lg[Lg < 0] = 0
            axes[0, 0].scatter(g[0], lut_.Lsurf[:, iaot, iwl, isza])
            axes[0, 0].plot(xx, Lsurf, label=sza)
            axes[0, 1].scatter(g[0], lut_.Lsky[:, iaot, iwl, isza])
            axes[0, 1].plot(xx, Lsky, label=sza)
            axes[1, 0].scatter(g[0], lut_.Lg[:, iaot, iwl, isza])
            axes[1, 0].plot(xx, Lg, label=sza, linestyle=':')
            axes[1, 1].scatter(g[0], lut_.Lsurf[:, iaot, iwl, isza] / lut_.Lsky[:, iaot, iwl, isza])
            color = next(axes[1, 1]._get_lines.prop_cycler)['color']
            yy = Lsurf / Lsky
            axes[1, 1].plot(xx, yy, color=color, label=sza)
            axes[1, 1].scatter(g[0],
                               (lut_.Lsurf[:, iaot, iwl, isza] + lut_.Lg[:, iaot, iwl, isza]) / lut_.Lsky[:, iaot, iwl,
                                                                                                isza], color=color)
            yy = (Lsurf + Lg) / Lsky
            axes[1, 1].plot(xx, yy, linestyle=':', color=color)

        axes[1, 1].legend(title=r'$\theta_s$ (deg)')
        axes[0, 0].set(ylabel=r'$L_{surf}$', ylim=self.set_axlims(lut_.Lsurf[:, iaot, iwl, :]))
        axes[0, 1].set(ylabel=r'$L_{sky}$')
        axes[1, 0].set(xlabel=r'Wind speed (m $s^{-1}$)', ylabel=r'$L_g$',
                       ylim=self.set_axlims(lut_.Lg[:, iaot, iwl, :]))
        axes[1, 1].set(xlabel=r'Wind speed (m $s^{-1}$)', ylabel=r'rho')
        fig.suptitle('wl: ' + str(g[2][iwl]) + 'nm; AOT: ' + str(g[1][iaot]))

        fig.tight_layout(rect=[0, 0., 1, 0.95])
        if fout != '':
            fig.savefig(fout + '_vs_wind_wl' + str(g[2][iwl]) + 'nm_aot' + str(g[1][iaot]) + '.png')

        xx = np.linspace(0, 80, 50)
        fig, ax = plt.subplots(2, 2, figsize=(10, 7))

        # rho_m1999 = pd.read_csv('./data/aux/rhoTable_Mobley1999.csv', skiprows=7)
        # rho_m2015 = pd.read_csv('./data/aux/rhoTable_Mobley2015.csv', skiprows=8)

        df = rho_m1999.query('vza == 40 & azi == 90')
        for label, df_ in df.groupby('wind'):
            if (label in [0, 2, 6, 10]):
                # df_.plot(x='sza', y='rho', ax=ax[0,0], label=label)
                ax[0, 0].plot(xx, si.spline(df_.sza, df_.rho, xx), label=label)

        df = rho_m2015.query('vza == 40 & azi == 90')
        for label, df_ in df.groupby('wind'):
            if (label in [0, 2, 6, 10]):
                # df_.plot(x='sza', y='rho', ax=ax[0,1], label=label)
                ax[0, 1].plot(xx, si.spline(df_.sza, df_.rho, xx), label=label)

        for wind in [0, 2, 6, 10]:
            label = wind
            Lsurf = si.RectBivariateSpline(g[0], g[3], lut_.Lsurf[:, iaot, iwl, :], kx=3)(wind,
                                                                                          xx)  # si.interpn((g[0],g[1]),lut_.Lsurf[:,:,3,isza], newgrid,method='splinef2d')
            Lsky = si.RectBivariateSpline(g[0], g[3], lut_.Lsky[:, iaot, iwl, :], kx=3)(wind,
                                                                                        xx)  # lut_.interp_lut(lut_.grid_lut,lut_.Lsky, newgrid)
            Lg = si.RectBivariateSpline(g[0], g[3], lut_.Lg[:, iaot, iwl, :], kx=3)(wind,
                                                                                    xx)  # lut_.interp_lut(lut_.grid_lut,lut_.Lg, newgrid)
            Lg[Lg < 0] = 0
            # axes[1,0].plot(xx,Lg)
            yy = (Lsurf[0, :]) / Lsky[0, :]
            ax[1, 0].plot(xx, yy, label=label)
            # yy = Lsurf / Lsky
            # axes[1,1].plot(xx,yy)
            # axes[1].plot(g[3],(lut_.Lsurf[iwind,iaot,iwl,:]+lut_.Lg[iwind,iaot,iwl,:])/lut_.Lsky[iwind,iaot,iwl,:], label=label)
            yy = (Lsurf[0, :] + Lg[0, :]) / Lsky[0, :]
            ax[1, 1].plot(xx, yy, label=label)

        ax[0, 0].legend(title='Wind (m/s)')
        ax[1, 0].legend(title='Wind (m/s)')
        ax[0, 0].set_xlabel('SZA (deg)')
        ax[0, 1].set_xlabel('SZA (deg)')
        ax[1, 0].set_xlabel('SZA (deg)')
        ax[1, 1].set_xlabel('SZA (deg)')
        ax[0, 0].set_ylabel('Rho factor')
        ax[1, 0].set_ylabel('Rho factor')
        ax[0, 0].set_title('Mobley 1999')
        ax[0, 1].set_title('Mobley 2015')
        ax[1, 0].set_title('Lsurf/Lsky')
        ax[1, 1].set_title('(Lsurf+Lg)/Lsky')
        fig.suptitle('wl: ' + str(g[2][iwl]) + 'nm; AOT: ' + str(g[1][iaot]))
        fig.tight_layout(rect=[0, 0., 1, 0.95])
        if fout != '':
            fig.savefig(fout + '_rho_tables_wl' + str(g[2][iwl]) + 'nm_aot' + str(g[1][iaot]) + '.png')


    def plot_lut_vs_wl(self, lut_, fout='', iaot=0, iwind=1):
        '''
        grid dimension [wind,aot,wl,sza]
        :param lut_:
        :param fout:
        :param iaot:
        :param iwind:
        :return:
        '''

        idx = 2 #for wavelength

        g = lut_.grid_lut

        xx = np.linspace(np.min(lut_.grid_lut[idx]), np.max(lut_.grid_lut[idx]), 50)
        newgrid = (xx, 1)
        isza = [5, 15, 30]
        winds = np.repeat(g[0][iwind], isza.__len__())
        gout = [xx, [g[1][iaot]], winds, g[3][isza]]
        Lsurf = lut_.spline_lut(g, lut_.Lsurf, gout)
        Lsky = lut_.spline_lut(g, lut_.Lsky, gout)
        Lg = lut_.spline_lut(g, lut_.Lg, gout)
        Lg[Lg < 0] = 0

        fig, axes = plt.subplots(2, 2, figsize=(10, 7))
        for isza in [5, 15, 30]:
            sza = g[3][isza]
            Lsurf = si.RectBivariateSpline(g[1], g[2], lut_.Lsurf[iwind, :, :, isza], kx=3)(g[1][iaot],xx )
            Lsky = si.RectBivariateSpline(g[1], g[2], lut_.Lsky[iwind, :,:, isza], kx=3)(g[1][iaot],xx )
            Lg = si.RectBivariateSpline(g[1], g[2], lut_.Lg[iwind,:, :, isza], kx=3)(g[1][iaot],xx )

            Lg[Lg < 0] = 0
            axes[0, 0].scatter(g[2], lut_.Lsurf[iwind, iaot, :, isza])
            axes[0, 0].plot(xx, Lsurf[0,:], label=sza)
            axes[0, 1].scatter(g[2], lut_.Lsky[iwind, iaot,:, isza])
            axes[0, 1].plot(xx, Lsky[0,:], label=sza)
            axes[1, 0].scatter(g[2], lut_.Lg[iwind, iaot, :, isza])
            axes[1, 0].plot(xx, Lg[0,:], label=sza, linestyle=':')
            axes[1, 1].scatter(g[2], lut_.Lsurf[iwind,iaot, :, isza] / lut_.Lsky[iwind, iaot, :, isza])
            color = next(axes[1, 1]._get_lines.prop_cycler)['color']
            yy = Lsurf[0,:] / Lsky[0,:]
            axes[1, 1].plot(xx, yy, color=color, label=sza)
            axes[1, 1].scatter(g[2],
                               (lut_.Lsurf[iwind, iaot, :, isza] + lut_.Lg[iwind, iaot, :, isza]) / lut_.Lsky[iwind, iaot, :,
                                                                                                isza], color=color)
            yy = (Lsurf[0,:] + Lg[0,:]) / Lsky[0,:]
            axes[1, 1].plot(xx, yy, linestyle=':', color=color)

        axes[1, 1].legend(title=r'$\theta_s$ (deg)')
        axes[0, 0].set(ylabel=r'$L_{surf}$', ylim=self.set_axlims(lut_.Lsurf[:, iaot, iwind, :]))
        axes[0, 1].set(ylabel=r'$L_{sky}$')
        axes[1, 0].set(xlabel=r'Wavelength (nm)', ylabel=r'$L_g$',
                       ylim=self.set_axlims(lut_.Lg[:, iaot, iwind, :]))
        axes[1, 1].set(xlabel=r'Wavelength (nm)', ylabel=r'rho')
        fig.suptitle('wind: ' + str(g[2][iwind]) + 'm/s ; AOT: ' + str(g[1][iaot]))

        fig.tight_layout(rect=[0, 0., 1, 0.95])
        if fout != '':
            fig.savefig(fout + '_vs_wavelength_wl' + str(g[0][iwind]) + 'nm_aot' + str(g[1][iaot]) + '.png')


        fig, axes = plt.subplots(2, 2, figsize=(10, 7))
        for isza in [5, 15, 30]:
            sza = g[3][isza]
            Lsurf = si.RectBivariateSpline(g[1], g[2], lut_.Lsurf[iwind, :, :, isza], kx=3)(g[1][iaot],xx )
            Lsky = si.RectBivariateSpline(g[1], g[2], lut_.Lsky[iwind, :,:, isza], kx=3)(g[1][iaot],xx )
            Lg = si.RectBivariateSpline(g[1], g[2], lut_.Lg[iwind,:, :, isza], kx=3)(g[1][iaot],xx )

            rho_lut = lut_.Lsurf/lut_.Lsky
            rho_g_lut = (lut_.Lsurf[iwind,iaot, :, isza] + lut_.Lg[iwind, iaot, :, isza])/ lut_.Lsky[iwind, iaot, :, isza]
            rho = si.RectBivariateSpline(g[1], g[2], rho_lut[iwind, :, :, isza], kx=3)(g[1],xx )


            Lg[Lg < 0] = 0

            axes[0, 0].scatter(g[2], rho_lut[iwind, 0, :, isza])
            axes[0, 0].plot(xx, rho[0,:], label=sza)
            axes[0, 0].set_title(g[1][0])
            axes[0, 1].scatter(g[2], rho_lut[iwind, 3, :, isza])
            axes[0, 1].plot(xx, rho[3,:], label=sza)
            axes[0, 1].set_title(g[1][3])
            axes[1, 0].scatter(g[2], rho_lut[iwind, 4, :, isza])
            axes[1, 0].plot(xx, rho[4,:], label=sza)
            axes[1, 0].set_title(g[1][4])
            axes[1, 1].scatter(g[2], rho_lut[iwind, 5, :, isza])
            axes[1, 1].plot(xx, rho[5,:], label=sza)
            axes[1,1].set_title(g[1][5])


        axes[1, 1].legend(title=r'$\theta_s$ (deg)')
        axes[0, 0].set(ylabel=r'$L_{surf}$', ylim=self.set_axlims(lut_.Lsurf[:, iaot, iwind, :]))
        axes[0, 1].set(ylabel=r'$L_{sky}$')
        axes[1, 0].set(xlabel=r'Wavelength (nm)', ylabel=r'$L_g$',
                       ylim=self.set_axlims(lut_.Lg[:, iaot, iwind, :]))
        axes[1, 1].set(xlabel=r'Wavelength (nm)', ylabel=r'rho')
        fig.suptitle('wind: ' + str(g[2][iwind]) + 'm/s ; AOT: ' + str(g[1][iaot]))

        fig.tight_layout(rect=[0, 0., 1, 0.95])
        if fout != '':
            fig.savefig(fout + '_vs_wavelength_wl' + str(g[0][iwind]) + 'nm_aot' + str(g[1][iaot]) + '.png')




        xx = np.linspace(0, 80, 50)
        fig, ax = plt.subplots(2, 2, figsize=(10, 7))

        # rho_m1999 = pd.read_csv('./data/aux/rhoTable_Mobley1999.csv', skiprows=7)
        # rho_m2015 = pd.read_csv('./data/aux/rhoTable_Mobley2015.csv', skiprows=8)

        df = rho_m1999.query('vza == 40 & azi == 90')
        for label, df_ in df.groupby('wind'):
            if (label in [0, 2, 6, 10]):
                # df_.plot(x='sza', y='rho', ax=ax[0,0], label=label)
                ax[0, 0].plot(xx, si.spline(df_.sza, df_.rho, xx), label=label)

        df = rho_m2015.query('vza == 40 & azi == 90')
        for label, df_ in df.groupby('wind'):
            if (label in [0, 2, 6, 10]):
                # df_.plot(x='sza', y='rho', ax=ax[0,1], label=label)
                ax[0, 1].plot(xx, si.spline(df_.sza, df_.rho, xx), label=label)

        for wind in [0, 2, 6, 10]:
            label = wind
            Lsurf = si.RectBivariateSpline(g[0], g[3], lut_.Lsurf[:, iaot, iwind, :], kx=3)(wind,
                                                                                          xx)  # si.interpn((g[0],g[1]),lut_.Lsurf[:,:,3,isza], newgrid,method='splinef2d')
            Lsky = si.RectBivariateSpline(g[0], g[3], lut_.Lsky[:, iaot, iwind, :], kx=3)(wind,
                                                                                        xx)  # lut_.interp_lut(lut_.grid_lut,lut_.Lsky, newgrid)
            Lg = si.RectBivariateSpline(g[0], g[3], lut_.Lg[:, iaot, iwind, :], kx=3)(wind,
                                                                                    xx)  # lut_.interp_lut(lut_.grid_lut,lut_.Lg, newgrid)
            Lg[Lg < 0] = 0
            # axes[1,0].plot(xx,Lg)
            yy = (Lsurf[0, :]) / Lsky[0, :]
            ax[1, 0].plot(xx, yy, label=label)
            # yy = Lsurf / Lsky
            # axes[1,1].plot(xx,yy)
            # axes[1].plot(g[3],(lut_.Lsurf[iwind,iaot,iwind,:]+lut_.Lg[iwind,iaot,iwind,:])/lut_.Lsky[iwind,iaot,iwind,:], label=label)
            yy = (Lsurf[0, :] + Lg[0, :]) / Lsky[0, :]
            ax[1, 1].plot(xx, yy, label=label)

        ax[0, 0].legend(title='Wind (m/s)')
        ax[1, 0].legend(title='Wind (m/s)')
        ax[0, 0].set_xlabel('SZA (deg)')
        ax[0, 1].set_xlabel('SZA (deg)')
        ax[1, 0].set_xlabel('SZA (deg)')
        ax[1, 1].set_xlabel('SZA (deg)')
        ax[0, 0].set_ylabel('Rho factor')
        ax[1, 0].set_ylabel('Rho factor')
        ax[0, 0].set_title('Mobley 1999')
        ax[0, 1].set_title('Mobley 2015')
        ax[1, 0].set_title('Lsurf/Lsky')
        ax[1, 1].set_title('(Lsurf+Lg)/Lsky')
        fig.suptitle('wl: ' + str(g[2][iwind]) + 'nm; AOT: ' + str(g[1][iaot]))
        fig.tight_layout(rect=[0, 0., 1, 0.95])
        if fout != '':
            fig.savefig(fout + '_rho_tables_wl' + str(g[2][iwind]) + 'nm_aot' + str(g[1][iaot]) + '.png')

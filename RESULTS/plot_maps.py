import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from netCDF4 import Dataset

from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], color='b', lw=2, label='PAN-AMAZONIA'),]

                #    Line2D([0], [0], marker='o', color='w', label='Scatter',
                #           markerfacecolor='g', markersize=15),
                #    Patch(facecolor='orange', edgecolor='r',
                #          label='Color Patch')]


var = ['avail_p','total_p','org_p','inorg_p', 'occ_p','mineral_p', 'tot_p']

raisg_mask = "/home/jdarela/Desktop/data_src/soil_map/tidy_data/predictor_data_raster/mask.shp"

mask = ShapelyFeature(Reader(raisg_mask).geometries(),
                                 ccrs.PlateCarree())

#mask = ShapelyFeature(raisg_mask, crs=ccrs.PlateCarree())

def open_dataset(vname, mean=True, tp=False):
    if not tp:
        fname = "predicted_" + vname + ".nc4"
    else:
        fname = "predictedTP_" + vname + ".nc4"
    fh = Dataset(fname)

    var = np.fliplr(fh.variables[vname][:])
    
    if mean:
        return var.mean(axis=0,)
    else:
        return var.std(axis=0,)


def calc_percentage(varn):
    pass


def calculate_mineral():
    # Estimate mineral + occluded pools
    org =  open_dataset("org_p")
    inorg =open_dataset("inorg_p")
    # occ = open_dataset("occ_p")
    avail =open_dataset("avail_p") 
    total =open_dataset("total_p") 

    out = total - (org + inorg + avail)

    return out

def plot_Pmap(vname):
    
    ##02 Define images & metadata to plot

    ##03 START Plot Annotations and for each vname

    m_p = False
    t_p = False
    units = "mg kg⁻¹"
    
    if vname == 'total_p':

        frac_of_total = None
        title = "Total P"
        nmodels = "n = 122"
        Aµ = "Aµ = 78.11 %"

    elif vname == 'tot_p':

        frac_of_total = None
        t_p = True

        title = "Total P - No disclosure data"
        img = open_dataset(vname, tp=t_p)
        nmodels = "n = 205"
        Aµ = "Aµ = 66.74 %"
    
    elif vname == 'avail_p':

        ds = Dataset("./predicted_avail_p_percent_of_tot.nc4")
        frac_of_total = np.flipud(ds.variables["avail_ppercent_of_total_p"][:])
        
        title = "Available P"
        nmodels = "n = 511"
        Aµ = "Aµ = 77.60 %"
    
    elif vname == 'org_p':
        
        ds = Dataset("./predicted_org_p_percent_of_tot.nc4")
        frac_of_total = np.flipud(ds.variables["org_ppercent_of_total_p"][:])
        
        title = "Organic P"
        nmodels = "n = 302"
        Aµ = "Aµ = 73.14 %"

    elif vname == 'inorg_p':
        
        ds = Dataset("./predicted_inorg_p_percent_of_tot.nc4")
        frac_of_total = np.flipud(ds.variables["inorg_ppercent_of_total_p"][:])
        
        title = "Secondary mineral P"
        nmodels = "n = 152"
        Aµ = "Aµ = 73.21 %"

    elif vname == 'occ_p':
  
        frac_of_total = None
        
        title = "Occluded P"
        nmodels = "n = 385"
        Aµ = "Aµ = 63.12 %"

    elif vname == 'mineral_p':

        ds = Dataset("./predicted_min-occ_over_total_p.nc4")
        frac_of_total = np.flipud(ds.variables["min1-occ_percent_of_total_p"][:])
        
        title = "Primary mineral P + Occluded P"
        nmodels = ""
        Aµ = ""
        img = calculate_mineral()
        m_p = True
  
    else:
        assert False, "not valid varname"
    
    ##03 END
    
    if not m_p and not t_p:
        img = open_dataset(vname)

    if not vname == "mineral_p" and not t_p:
        SD = np.flipud(Dataset("./predicted_%s_std.nc4" % vname).variables[vname + "_SD"])
    
    if t_p:
        SD = np.flipud(Dataset("./predictedTP_tot_p_std.nc4").variables["tot_p_SD"])

    # TODO @OK
    ## 04 START plots fraction/total_p ratio
    # Implemented in the if-elif block - @frac_of_total
    ## 04 END

    ## 05 START read accuracy?
    
    ## 05 END
    
    ## 02 END
    
    ## ---------PLOT MAP-----------------
    # Raster extent
    img_proj = ccrs.PlateCarree()
    img_extent = [-180, 180, -90, 90]

    fig = plt.figure(figsize=(10, 5))
    gs = gridspec.GridSpec(1, 2)
    ax = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
    
    # ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())  
    ax.set_xticks([-70, -45], crs=ccrs.PlateCarree())
    ax.set_yticks([-17, 10], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True, number_format='g')
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    
    ax.set_title(title)   
    ax.set_extent([-81.5, -41.5, -23.5, 14.5], crs=ccrs.PlateCarree())
    
    imsh = plt.imshow(img, transform=img_proj, extent=img_extent, cmap='nipy_spectral')   
    cbar = fig.colorbar(imsh, ax=ax, extend='both', orientation='vertical',  spacing='proportional', shrink=0.7)
    cbar.ax.set_ylabel(units)
    cbar.minorticks_on()
    ax.add_feature(mask, edgecolor='b', linewidth=2, facecolor="None")
    ax.add_feature(cfeature.BORDERS)
    ax.coastlines(resolution='110m', linewidth=1)
    
    ax.legend(handles=legend_elements, loc=("best"), fontsize= 'small')

    ax.annotate("%s\n%s"%(nmodels, Aµ), xy=(93, 79), xycoords='figure points', horizontalalignment='left',
                verticalalignment='bottom', fontsize="small")
    
    if t_p:
        ax1 = fig.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
        ax1.set_xticks([-70, -45], crs=ccrs.PlateCarree())
        #ax1.set_yticks([-17, 10], crs=ccrs.PlateCarree())
        ax1.xaxis.set_major_formatter(lon_formatter)
        ax1.set_extent([-81.5, -41.5, -23.5, 14.5], crs=ccrs.PlateCarree())
        imsh1 = plt.imshow(SD, transform=img_proj, extent=img_extent, cmap='viridis')
        cbar1 = fig.colorbar(imsh1, ax=ax1, extend='both', orientation='vertical',  spacing='proportional', shrink=0.7)
        cbar1.ax.set_ylabel("Standard deviation")
        cbar1.minorticks_on()
        ax1.add_feature(mask, edgecolor='b', linewidth=2, facecolor="None")
        ax1.add_feature(cfeature.BORDERS)
        ax1.coastlines(resolution='110m', linewidth=1)
        ax1.set_title("Model agreement")

    elif frac_of_total is not None:
        ax1 = fig.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
        ax1.set_xticks([-70, -45], crs=ccrs.PlateCarree())
        #ax1.set_yticks([-17, 10], crs=ccrs.PlateCarree())
        ax1.xaxis.set_major_formatter(lon_formatter)
        ax1.set_extent([-81.5, -41.5, -23.5, 14.5], crs=ccrs.PlateCarree())
        imsh1 = plt.imshow(frac_of_total, transform=img_proj, extent=img_extent, cmap='magma')
        cbar1 = fig.colorbar(imsh1, ax=ax1, extend='both', orientation='vertical',  spacing='proportional', shrink=0.7)
        cbar1.ax.set_ylabel("%")
        cbar1.minorticks_on()
        ax1.add_feature(mask, edgecolor='b', linewidth=2, facecolor="None")
        ax1.add_feature(cfeature.BORDERS)
        ax1.coastlines(resolution='110m', linewidth=1)
        ax1.set_title("Fraction of total P")
    
    elif vname == 'total_p':
        ax1 = fig.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
        ax1.set_xticks([-70, -45], crs=ccrs.PlateCarree())
        #ax1.set_yticks([-17, 10], crs=ccrs.PlateCarree())
        ax1.xaxis.set_major_formatter(lon_formatter)
        ax1.set_extent([-81.5, -41.5, -23.5, 14.5], crs=ccrs.PlateCarree())
        imsh1 = plt.imshow(SD, transform=img_proj, extent=img_extent, cmap='viridis')
        cbar1 = fig.colorbar(imsh1, ax=ax1, extend='both', orientation='vertical',  spacing='proportional', shrink=0.7)
        cbar1.ax.set_ylabel("Standard deviation")
        cbar1.minorticks_on()
        ax1.add_feature(mask, edgecolor='b', linewidth=2, facecolor="None")
        ax1.add_feature(cfeature.BORDERS)
        ax1.coastlines(resolution='110m', linewidth=1)
        ax1.set_title("Model agreement")
    
    # plt.tight_layout()
    fig.subplots_adjust(wspace=0.07)
    plt.plot()
    plt.savefig("/home/jdarela/Área de Trabalho/p_figs/%s.png" %vname, dpi=500)
    plt.show()

def plot_bar():
    
    import pandas as pd
    
    def bplot(t_p=False):

        if t_p:
            data = pd.read_csv("importances_tot_p.csv")

            f = plt.figure(figsize=(12, 5))
            #gs = gridspec.GridSpec(1, 1)
            ax1 = f.add_subplot(111)

            ax1.set_title("Total P - unpublished data")
            ax1.set_xlabel("Importance")
            ax1.set_ylabel("Features")
            data.boxplot(ax=ax1, sym='', vert=True, whis=[0.5,99.5], widths=0.7, rot=45)
            plt.tight_layout()
            plt.savefig("/home/jdarela/Área de Trabalho/p_figs/boxplot_imp_tot_p2.png", dpi=500)
            plt.show()
        
        else:
            
            titles = ['Total P','Available P','Organic P','Secondary mineral P']
            
            data1 = pd.read_csv("importances_total_p.csv")
            data2 = pd.read_csv("importances_avail_p.csv")
            data3 = pd.read_csv("importances_org_p.csv")
            data4 = pd.read_csv("importances_inorg_p.csv")

            f, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=1, ncols=4, sharex=True, sharey=True)
            f.set_figheight(10)
            f.set_figwidth(10)
            
            # AX 1 
            ax1.set_title(titles[0])
            #ax1.set_xlabel("Importance")
            ax1.set_ylabel("Features")
            data1.boxplot(ax=ax1, sym='', vert=False, whis=[0.5,99.5], widths=0.7, rot=45)
            
            # AX 2 
            ax2.set_title(titles[1])
            #ax2.set_xlabel("Importance")
            #ax2.set_ylabel("Features")
            data2.boxplot(ax=ax2, sym='', vert=False, whis=[0.5,99.5], widths=0.7)

            # AX 3 
            ax3.set_title(titles[2])
            #ax3.set_xlabel("Importance")
            #ax3.set_ylabel("Features")
            data3.boxplot(ax=ax3, sym='', vert=False, whis=[0.5,99.5], widths=0.7)

            # AX 4 
            ax4.set_title(titles[3])
            #ax4.set_xlabel("Importance")
            #ax4.set_ylabel("Features")
            data4.boxplot(ax=ax4, sym='', vert=False, whis=[0.5,99.5], widths=0.7)
            
            f.subplots_adjust(wspace=0.01)
        
        plt.tight_layout()
        plt.savefig("/home/jdarela/Área de Trabalho/p_figs/boxplot_importances.png", dpi=500)
        plt.show()

    
    bplot(t_p=False)
    #bplot(t_p=True)

def plot_std(var):
    
    if var == "avail_p":
        SD = np.flipud(Dataset("./predicted_avail_p_std.nc4").variables["avail_p_SD"])
        title = "Available P"
    elif var == "org_p":
        SD = np.flipud(Dataset("./predicted_org_p_std.nc4").variables["org_p_SD"])
        title = "Organic P"
    elif var == "inorg_p":
        SD = np.flipud(Dataset("./predicted_inorg_p_std.nc4").variables["inorg_p_SD"])
        title = "Secondary mineral P"
    else:
        assert False, "VAR NAOo Val3"
    
    legend_elements = [Line2D([0], [0], color='b', lw=2, label='PAN-AMAZONIA'),]

    img_proj = ccrs.PlateCarree()
    img_extent = [-180, 180, -90, 90]

    fig = plt.figure(figsize=(5, 5))
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
    
    # ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())  
    ax.set_xticks([-70, -45], crs=ccrs.PlateCarree())
    ax.set_yticks([-17, 10], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True, number_format='g')
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    
    ax.set_title(title)   
    ax.set_extent([-81.5, -41.5, -23.5, 14.5], crs=ccrs.PlateCarree())
    
    imsh = plt.imshow(SD, transform=img_proj, extent=img_extent, cmap="viridis")   
    cbar = fig.colorbar(imsh, ax=ax, extend='both', orientation='vertical',  spacing='proportional', shrink=0.80)
    cbar.ax.set_ylabel("Standard deviation")
    cbar.minorticks_on()
    ax.add_feature(mask, edgecolor='b', linewidth=2, facecolor="None")
    ax.add_feature(cfeature.BORDERS)
    ax.coastlines(resolution='110m', linewidth=1)

    ax.legend(handles=legend_elements, loc=("best"), fontsize="small")
    plt.savefig("/home/jdarela/Área de Trabalho/p_figs/sd_%s.png" % var, dpi=500)
    plt.show()



if __name__ == '__main__':
    
    # # PLot importances
    plot_bar()
    
    # # PLot maps
    # for v in var:
    #     plot_Pmap(v)
    
    # # PLot stds for other variables
    # vs = ["avail_p", "org_p", "inorg_p"]
    # for v in vs:
    #     plot_std(v)
import os
from glob import glob1
import numpy as np
from netCDF4 import Dataset

from table2raster import save_nc

"""Calculate MEANS, SD and proportions of P fractions"""

def open_dataset(vname, mean=True, tp=False):

    """Open the dataset and calculate mean or SD"""
    
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


def calculate_mineral():
    """ Estimate mineral + occluded pools"""

    org =  open_dataset("org_p")
    inorg =open_dataset("inorg_p")
    # occ = open_dataset("occ_p")
    avail =open_dataset("avail_p") 
    total =open_dataset("total_p")

    # TODO 
    ## Quantificar a variabilidade/incerteza
    
    return total - (org + inorg + avail)


files = glob1(os.getcwd(), "*.nc4")

total_p = open_dataset('total_p')

for fh in files:
    t_p = False
    if fh == "predictedTP_tot_p.nc4":
        t_p = True
        n = 12
    else:
        n = 10
        t_p = False
    varn = fh[n:].split('.')[0]
    print(varn)

    # CALCULATE THE CONFIDENCE
    # All ensemble show high agreement among models - mean > 2 SD 

    MEAN = open_dataset(varn, tp=t_p)
    SD = open_dataset(varn, mean=False, tp=t_p)
    
    # High confidence
    result = MEAN > (4.0 * SD)


    fname = fh.split(".")[0] + "_confidence.nc4"
    save_nc(fname, result, varn + "_SDMEAN", ndim=None)
    
    # CALCULATE THE PERNTAGES OF TOTAL P FOR OTHER FRACTIONS
    if varn in ["tot_p", "total_p", "occ_p"]:
        continue
    else:
        fname = fh.split(".")[0] + "_percent_of_tot.nc4"
        dt = open_dataset(varn)
        result = (dt / total_p) * 100.0
        save_nc(fname, result, varn + "percent_of_total_p", ndim=None)

mineral = calculate_mineral()
prop = (mineral / total_p) * 100.0
fname = "predicted_min-occ_over_total_p.nc4"
save_nc(fname, prop, 'min1-occ_' + "percent_of_total_p", ndim=None)

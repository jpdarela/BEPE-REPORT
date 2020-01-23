import glob
import numpy as np
import pandas as pd

mode = 'total'
diff = 'TP'
VARNAME = "inorg_p"

if mode == 'fractions':

    from rforest_test import feat_list as names
    from rforest_test import label_name as varn
    output = "./predicted_P_%s/" % varn
    names = names + [varn,]
    diff = ''
elif mode == 'total':
    
    from rforest_test2 import feat_list as names
    from rforest_test2 import label_name as varn

    label_name = "tot_p"
    output = "./predictedTP_P_%s/" % label_name
    model = "modelsTP_"
    names = names + [varn,]
    diff = 'TP'
else:
    from rforest_test import feat_list as names
    varn = VARNAME
    output = "./predicted_P_%s/" % varn
    names = names + [varn,]
    diff = ''


def col2arr(filename, varn, names):

    datan = pd.read_csv(filename)
    indexn = np.arange(datan.shape[0],dtype=np.int32)
    
    outn = np.zeros(shape=(360,720),dtype=np.float32) - 9999.0

    for i in indexn:
        if False: #datan.iloc[i]['forest'] == 0:
            continue
        else:
            nx = datan.iloc[i]['nx']
            ny = datan.iloc[i]['ny']
            data = datan.iloc[i][names[varn]]
            outn[np.int32(ny), np.int32(nx)] = data
            
    return np.ma.masked_array(outn, outn == -9999.0, fill_value=-9999.0), names[varn]


def save_nc(fname, arr, varname, ndim=None, axis_data=[0,]):
    
    from netCDF4 import Dataset

    nc_filename = fname

    rootgrp = Dataset(nc_filename, mode='w', format='NETCDF4')

    la = arr.shape[0]
    lo = arr.shape[1]
    
    if ndim:
        la = arr.shape[1]
        lo = arr.shape[2]
        rootgrp.createDimension("models", ndim)

        #dimensions
    rootgrp.createDimension("latitude", la)
    rootgrp.createDimension("longitude", lo)
        #variables

    latitude = rootgrp.createVariable(varname="latitude",
                                      datatype=np.float32,
                                      dimensions=("latitude",))

    longitude = rootgrp.createVariable(varname="longitude",
                                       datatype=np.float32,
                                       dimensions=("longitude",))
    if ndim is not None:
        model = rootgrp.createVariable(varname="models",
                                   datatype=np.int32,
                                   dimensions=("models",))
    
    
        var_ = rootgrp.createVariable(varname = varname,
                                  datatype=np.float32,
                                  dimensions=("models", "latitude","longitude",),
                                  fill_value=-9999.0)
    else:
        var_ = rootgrp.createVariable(varname = varname,
                                  datatype=np.float32,
                                  dimensions=("latitude","longitude",),
                                  fill_value=-9999.0)

        #attributes
        ## rootgrp
    rootgrp.description =  'Phosphorus fractions'
    rootgrp.source = "darelafilho@gmail.com"
    
    ## lat
    latitude.units = u"degrees_north"
    latitude.long_name=u"latitude"
    latitude.standart_name =u"latitude"
    latitude.axis = u'Y'
    
    ## lon
    longitude.units = "degrees_east"
    longitude.long_name = "longitude"
    longitude.standart_name = "longitude"
    longitude.axis = 'X'
    
    ## models
    if ndim is not None:
        model.units = u"units"
        model.long_name = u"Modelos selecionados por desempenho maior que 70 % acc"
        model.axis = "T"

    ## var
    var_.long_name = varname
    var_.units = 'mg kg-1'
    var_.standard_name= varname
    var_.missing_value=-9999.0
    
    ## WRITING DATA
    longitude[:] = np.arange(-179.75, 180, 0.5)
    latitude[:] =  np.arange(-89.75, 90, 0.5)

    if ndim is not None:
        model[:] = np.array(axis_data, dtype=np.int32)
        var_[:, :, :] = np.fliplr(arr)
    else:
        var_[:,:] = np.flipud(arr)
    rootgrp.close()

if __name__ == "__main__":
    folder = output
    files = glob.glob1(folder, "*.csv")
    nmodels = int(len(files))
    output_arr = np.zeros(shape=(nmodels,360,720),dtype=np.float32) - 9999.0
    out = []
    model_r_states = []
    for i, fh in enumerate(files):
        filename_store = fh
        model_r_states.append(fh.split('.')[0].split('_')[-1])
        arr = col2arr(output + fh, -1, names)
        out.append(arr[0])
        output_arr[i,:,:] = arr[0].__array__()
    
    output_arr = np.ma.masked_array(output_arr, output_arr == -9999.0)

    mean_arr = output_arr.mean(axis=0,)
    std_arr = output_arr.std(axis=0,)

    frac = filename_store.split('.')[0].split('_')[1]
    de_que = filename_store.split('.')[0].split('_')[2]

    fname = filename_store.split('.')[0].split('_')[0] + diff + "_" + frac + "_" + de_que + ".nc4"
    save_nc(fname, output_arr, varn, ndim=len(model_r_states), axis_data=model_r_states)
    #fnamestd = filename_store.split('.')[0].split('_')[0] + "_" + frac + "_" + de_que + "_std_" + ".nc4"
    #fnamemean = filename_store.split('.')[0].split('_')[0] + "_" + frac + "_" + de_que + "_mean_" + ".nc4"
    # save_nc(fnamestd, std_arr, varn)
    # save_nc(fnamemean, mean_arr, varn)

#(fname, arr, varname, nmodels=None, r_state=None, acc=None)
# predicted_occ_p_model_89707.csv
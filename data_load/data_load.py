import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate.interpolate import make_interp_spline


#
# path = r"RECO_data"
#
# FileNames =os.listdir(path)

def data_load():
    path = r"../RECO_data"
    # print(os.listdir(path))
    # path = 'RECO_data'
    FileNames = os.listdir(path)
    # print(FileNames)
    x = pd.DataFrame()
    for name in  FileNames:

        if re.search('Load',name):
            full_name =os.path.join(path,name)
            pd_load =pd.read_csv(full_name,encoding='utf-8')
            pd_load = pd_load['mw'].tolist()
        elif re.search('jcpl',name):
            full_name = os.path.join(path, name)
            data = pd.read_csv(full_name,encoding='utf-8')
            x= pd.concat([x,data])
            pd_price= x['JCPL'].tolist()
            for i in  range(len(x)):
                if float(pd_price[i].strip("$")) >100:
                    pd_price[i]  =60/600+0.15
                else:
                    pd_price[i] = float(pd_price[i].strip("$"))/600+0.15
        else:
            full_name = os.path.join(path,name)

            pd_wea = pd.read_csv(full_name,encoding='utf-8')
            pd_wea_T = pd_wea['气温℃'].tolist()
            pd_wea_G_dir = pd_wea['直接辐射W/m^2'].tolist()
            pd_wea_G_diff = pd_wea['散射辐射W/m^2'].tolist()
            pd_wea_wind = pd_wea['地面风速m/s'].tolist()

            pd_wea_G_hor = pd_wea['地表水平辐射W/m^2'].tolist()

    return pd_load,pd_price,pd_wea_wind,pd_wea_G_dir,pd_wea_G_diff,pd_wea_T,pd_wea_G_hor


def H2_price():
    x = []
    for i in range(8760):

        x.append(i)

    return x




if __name__ == '__main__':
    pd_load,pd_ResGrid_price,pd_wea_wind,pd_wea_G_dir,pd_wea_G_diff,pd_wea_T ,pd_wea_G_hor= data_load()
    # pd_price1 =price_reset(pd_price)
    dist_price = list(range(len(pd_ResGrid_price)))
    h2_price = H2_price()

    # plt.plot(dist_price,pd_price1)
    # plt.show()
    plt.plot(dist_price,pd_ResGrid_price)



    # fig,([axs3,axs4],[axs5,axs6]) = plt.subplots(2,2)
    #
    # # axs1.plot(dist_price,pd_price)
    # # axs1.set_xlabel('Time [h]')
    # # axs1.set_ylabel('Price [$/kwh]')
    # # axs1.set_title('Power_price ')
    # # #
    # # #
    # # #
    # # #
    # # pd_load =pd_load[:504]
    # # dist_load = list(range(len(pd_load)))
    # # axs2.plot(dist_load,pd_load)
    # # axs2.set_xlabel('Time [h]')
    # # axs2.set_ylabel('Load [kwh]')
    # # axs2.set_title('Power_load ')
    #
    # dist_G_dir = list(range(len(pd_wea_G_dir)))
    # axs3.plot(dist_G_dir,pd_wea_G_dir)
    # axs3.set_xlabel('Time [h]')
    # axs3.set_ylabel('solar irradiance dir [W/m²]')
    # axs3.set_title('solar irradiance dir ')
    #
    # dist_G_dif = list(range(len(pd_wea_G_diff)))
    # axs4.plot(dist_G_dif,pd_wea_G_diff)
    # axs4.set_xlabel('Time [h]')
    # axs4.set_ylabel('solar irradiance diff [W/m²]')
    # axs4.set_title('solar irradiance diff ')
    #
    #
    # dist_wind = list(range(len(pd_wea_wind)))
    # axs5.plot(dist_wind,pd_wea_wind)
    # axs5.set_xlabel('Time [h]')
    # axs5.set_ylabel('wind speed [m/s]')
    # axs5.set_title('wind speed ')
    #
    # dist_G_hor = list(range(len(pd_wea_G_hor)))
    # axs6.plot(dist_G_hor,pd_wea_G_hor)
    # axs6.set_xlabel('Time [h]')
    # axs6.set_ylabel('solar irradiance hor [W/m²]')
    # axs6.set_title('solar irradiance hor ')
    # #
    # #
    # fig.subplots_adjust(wspace=0.5,hspace=0.5)
    # plt.savefig('price_data.svg', format='svg')

    plt.show()



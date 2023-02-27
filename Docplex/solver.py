from docplex.mp import model
import numpy as np
from System.PV import PVSystem
from data_load.data_load import data_load
from System.wind import windpower
import matplotlib.pyplot as plt



def min_cost(per_pv_cost,per_wind_cost,pv_om_fix,wind_om_fix,sto_charge_cost,sto_discharge_cost,
             sto_energy_cost,sto_om_fix,sto_om,load,grid_price,timeload,pv_om,wind_om,res_rate,
             eff_ch,eff_dis
             ):
    load = load
    '''


    :param per_pv_cost: int
    :param per_wind_cost:int
    :param pv_om_fix:float
    :param wind_om_fix:float
    :param sto_charge_cost:int
    :param sto_discharge_cost:int
    :param sto_energy_cost:int
    :param sto_om_fix:float
    :param pv_power:int
    :param wind_power:int
    :param sto_om:int
    :return:
    '''
    '''
    var set
    
    '''
    model1 = model.Model()
    pv_cap =model1.integer_var(name='pv_cap',lb=0)
    wind_cap = model1.integer_var(name='wind_cap',lb=0)
    sto_charge  =model1.integer_var(name='sto_charge',lb=0)
    sto_discharge = model1.integer_var(name='sto_discharge',lb=0)
    sto_cap = model1.integer_var(name='sto_cap',lb=0)

    grid_power = model1.continuous_var_list([i for i in range(timeload)],name='grid_power',lb=0)
    sto_inj = model1.continuous_var_list([i for i in range(timeload)], name='sto_inj', lb=0)
    sto_wdw = model1.continuous_var_list([i for i in range(timeload)], name='sto_wdw', lb=0)
    sto_lvl= model1.continuous_var_list([i for i in range(timeload)], name='sto_lvl', lb=0)

    'data_set'
    pv_power = PVSystem(P_PV_rated=pv_cap)
    wind_power = windpower(wind_cap)
    pv_all  = 0
    wind_all =0


    for i in range(timeload):
        pv_all+=pv_power.PVpower(i)
        wind_all +=wind_power[i]
    '''
    cons set
    '''

    ' demoand balance'
    for i in range(timeload):
        model1.add_constraint(sto_inj[i]-sto_wdw[i]+pv_power.PVpower(i)+wind_power[i] +grid_power[i] ==load[i] )
    'policy set'
    model1.add_constraint(pv_all+wind_all>=res_rate*(model1.sum(grid_power[:timeload])+pv_all+wind_all))

    'sto balance'
    for i  in range(timeload-1):
        model1.add_constraint(sto_lvl[i+1] - sto_lvl[i] ==eff_ch*sto_wdw[i]-sto_inj[i]/eff_dis )

    'sto ch > sto dis'
    for i in range(timeload):
        model1.add_constraint(model1.sum(sto_wdw[:i]) >=model1.sum(sto_inj[:i]))


    for i  in range(timeload):
        model1.add_constraint(sto_lvl[i]<=sto_cap)
        model1.add_constraint(sto_inj[i]<=sto_discharge)
        model1.add_constraint(sto_wdw[i] <=sto_charge)










    '''
    obj set
    '''
    obj_inv = pv_cap*per_pv_cost+wind_cap*per_wind_cost+sto_charge*sto_charge_cost+sto_discharge*sto_discharge_cost+\
    sto_cap*sto_energy_cost+pv_cap*pv_om_fix+wind_cap*wind_om_fix+sto_om_fix*sto_cap

    obj_om = 0
    for i in range(timeload):
        obj_om  += (sto_inj[i]+sto_wdw[i])*sto_om+grid_power[i]*grid_price[i]+pv_power.PVpower(i)*pv_om+\
            wind_power[i]*wind_om
    model1.add_constraint(pv_cap<=1000)
    model1.add_constraint(wind_cap<=1000)

    # solution = model1.minimize(obj_om+obj_inv)
    model1.minimize(obj_inv+obj_om)
    solution  =model1.solve()
    print('-------------------------------')
    print(timeload,'timeload ')
    print(solution.solve_details)

    return solution.get_value(pv_cap),solution.get_value(sto_charge),solution.get_value(sto_discharge),solution.get_value(sto_cap)\
,solution.get_values(grid_power),solution.get_values(sto_inj),solution.get_values(sto_wdw),solution.get_values(sto_lvl)


if __name__ == '__main__':
    pd_load, pd_ResGrid_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

    pv_cap,sto_charge,sto_discharge,sto_cap,grid_power,sto_inj,sto_wdw,sto_lvl =min_cost(per_pv_cost=6950,per_wind_cost=10311,pv_om_fix=1000,wind_om_fix=1000,sto_charge_cost=1743,sto_energy_cost=1190,sto_om_fix=500,sto_om=200,
                   load=pd_load,grid_price=pd_ResGrid_price,timeload=507,sto_discharge_cost=1743,pv_om=100,wind_om=100,res_rate=0.7
                   ,eff_dis=0.9,eff_ch=0.9)
    dis_list =list(range(len(grid_power)))

    '''
    PV+Grid_output
    timeload = 168
    '''
    x = PVSystem(P_PV_rated=pv_cap)
    print(len(grid_power))
    plt.plot(dis_list,grid_power,label ="Grid")
    # plt.legend()
    pv_power =x.draw_polt(len(grid_power))
    plt.plot(dis_list,pv_power,label ='PV')
    plt.xlabel('Time [h]')
    plt.ylabel('Power [kw]')
    plt.title('PV or grid output')
    plt.legend()

    plt.plot(dis_list,sto_inj,label='Battery')
    plt.legend()

    plt.savefig('Power_output.svg', format='svg')
    plt.clf()
    '''
    电池充放电
    timeload =507
    '''
    plt.plot(dis_list,sto_inj,label='Battery_discharge')

    plt.xlabel('Time [h]')
    plt.ylabel('Power [kw]')
    plt.title('Battery charge/discharge')
    plt.legend()

    plt.plot(dis_list, sto_wdw, label='Battery_charge')
    plt.xlabel('Time [h]')
    plt.ylabel('Power [kw]')
    plt.legend()

    plt.savefig('Battery.svg', format='svg')
    plt.clf()
    '''
    x_lvl
    
    timeload =8200
    '''
    plt.plot(dis_list, sto_lvl, label='Battery_energy')
    plt.xlabel('Time [h]')
    plt.ylabel('Power [kwh]')
    plt.title('Battery energy')
    plt.legend()


    plt.savefig('energy.svg', format='svg')
    plt.clf()


    '''
    H2 
    '''
    pv_cap,sto_charge,sto_discharge,sto_cap,grid_power,sto_inj,sto_wdw,sto_lvl =min_cost(per_pv_cost=6950,per_wind_cost=10311,pv_om_fix=1000,wind_om_fix=1000,sto_charge_cost=4200,sto_energy_cost=328,sto_om_fix=100,sto_om=50,
                   load=pd_load,grid_price=pd_ResGrid_price,timeload=168,sto_discharge_cost=1190,pv_om=100,wind_om=100,res_rate=0.7
                   ,eff_dis=0.7,eff_ch=0.90)
    dis_list =list(range(len(grid_power)))
    x = PVSystem(P_PV_rated=pv_cap)
    print(len(grid_power))
    plt.plot(dis_list,grid_power,label ="Grid")

    pv_power =x.draw_polt(len(grid_power))
    plt.plot(dis_list,pv_power,label ='PV')
    plt.xlabel('Time [h]')
    plt.ylabel('Power [kw]')
    plt.title('PV or grid output')
    plt.legend()

    plt.plot(dis_list,sto_inj,label='H2')
    plt.legend()

    plt.savefig('H2 Power_output.svg', format='svg')
    plt.clf()


    pv_cap,sto_charge,sto_discharge,sto_cap,grid_power,sto_inj,sto_wdw,sto_lvl =min_cost(per_pv_cost=6950,per_wind_cost=10311,pv_om_fix=1000,wind_om_fix=1000,sto_charge_cost=4200,sto_energy_cost=328,sto_om_fix=100,sto_om=50,
                   load=pd_load,grid_price=pd_ResGrid_price,timeload=507,sto_discharge_cost=1190,pv_om=100,wind_om=100,res_rate=0.7
                   ,eff_dis=0.7,eff_ch=0.90)
    dis_list = list(range(len(grid_power)))
    plt.plot(dis_list,sto_inj,label='FC_discharge')

    plt.xlabel('Time [h]')
    plt.ylabel('Power [kw]')
    plt.title('H2 charge/discharge')
    plt.legend()

    plt.plot(dis_list, sto_wdw, label='H2_charge')
    plt.xlabel('Time [h]')
    plt.ylabel('Power [kw]')
    plt.legend()

    plt.savefig('H2.svg', format='svg')
    plt.clf()


    pv_cap,sto_charge,sto_discharge,sto_cap,grid_power,sto_inj,sto_wdw,sto_lvl =min_cost(per_pv_cost=6950,per_wind_cost=10311,pv_om_fix=1000,wind_om_fix=1000,sto_charge_cost=4200,sto_energy_cost=328,sto_om_fix=100,sto_om=50,
                   load=pd_load,grid_price=pd_ResGrid_price,timeload=507,sto_discharge_cost=1190,pv_om=100,wind_om=100,res_rate=0.7
                   ,eff_dis=0.7,eff_ch=0.90)
    dis_list = list(range(len(grid_power)))
    plt.plot(dis_list, sto_lvl, label='H2_energy')
    plt.xlabel('Time [h]')
    plt.ylabel('Power [kwh]')
    plt.title('H2 energy')
    plt.legend()
    plt.savefig('H2 Energy.svg', format='svg')
    plt.clf()
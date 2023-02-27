from docplex.mp import model
from data_load.data_load import data_load

def min_cost(timeload,load,gen_pv_max,gen_wind_max,sto_energy_max,sto_charge_max,sto_dis_max,k_up,k_down,min_power,max_power,
             eff_ch,eff_dis,max_h,min_h,per_cost_pv,per_cost_wind,per_cost_sto_energy,per_cost_sto_charge,per_cost_sto_dis,
             om_pv,om_wind,om_sto,om_ch,om_dis,sto_in_po,res_price):

    model_l = model.Model()
    Load =load

    'var set integer'
    gen_pv_rate =model_l.integer_var(lb=0,name='pv')
    gen_wind_rate = model_l.integer_var(lb=0,name='wind')

    sto_energy =model_l.integer_var(lb=0,name= 'sto')

    sto_charge =model_l.integer_var(lb=0,name='sto_cha')

    sto_dis  =model_l.integer_var(lb=0,name='sto_dis')
    sto_time =model_l.integer_var(lb=0,name='sto_time')

    'var set '

    x_gen_in = model_l.continuous_var_list([i for i in range(timeload)],lb=0,name='gen_injc')

    x_sto_in = model_l.continuous_var_list([i for i in range(timeload)],name='x',lb=0 )

    x_sto_wdw =model_l.continuous_var_list([i for i in range(timeload)],name='x2',lb=0 )

    x_fuel_in = model_l.continuous_var_list([i for  i in range(timeload)],lb=0,name='fuel_in')

    x_lvl = model_l.continuous_var_list([i for i in range(timeload)],lb=0,name='soc')
    x_fuel_in_sto =model_l.continuous_var_list([i for  i in range(timeload)],lb=0,name='fuel_in_sto')


    'const set'
    model_l.add_constraint(gen_pv_rate<= gen_pv_max)
    model_l.add_constraint(gen_wind_rate <=gen_wind_max)
    model_l.add_constraint(sto_energy <=sto_energy_max)
    model_l.add_constraint(sto_charge <=sto_charge_max)
    model_l.add_constraint(sto_dis <=sto_dis_max)
    model_l.add_constraint(sto_time <=max_h)
    model_l.add_constraint(min_h<=sto_time)
    model_l.add_constraint((gen_pv_rate+gen_pv_rate)*sto_time <=sto_energy)


    for i in range(timeload):
        model_l.add_constraint(x_sto_wdw[i] <=sto_charge)
        model_l.add_constraint(x_gen_in[i]+x_sto_in[i]+x_fuel_in[i]-x_sto_wdw[i] == Load[i])
        model_l.add_constraint(x_gen_in[i]+x_fuel_in[i]+x_sto_in[i] <= max_power)
        model_l.add_constraint(min_power<=x_gen_in[i]+x_fuel_in[i]+x_sto_in[i])
        model_l.add_constraint(x_lvl[i] <= (gen_pv_rate+gen_wind_rate)*sto_time)
        model_l.add_constraint(x_sto_wdw[i]<=x_lvl[i]*eff_dis)
        model_l.add_constraint(x_sto_wdw[i]+x_sto_in[i] <= gen_pv_rate+gen_wind_rate+x_fuel_in_sto[i]+x_fuel_in[i])
        model_l.add_constraint(x_lvl[i]<=sto_energy)
        model_l.add_constraint(x_sto_wdw[i]<= sto_charge)


        if i<(timeload-1):
            model_l.add_constraint(x_gen_in[i+1]+x_fuel_in[i+1]+x_sto_in[i+1] -x_gen_in[i] - x_fuel_in[i] - x_gen_in[i] <=k_up*(gen_pv_rate+gen_wind_rate+sto_dis)  )
            model_l.add_constraint(x_gen_in[i]+x_fuel_in[i]+x_sto_in[i] -x_gen_in[i+1] - x_fuel_in[i+1] - x_gen_in[i+1] <=k_down*(gen_pv_rate+gen_wind_rate+sto_dis))
            model_l.add_constraint(x_lvl[i+1] - x_lvl[i]    == x_sto_wdw[i]*eff_ch + x_fuel_in_sto[i]*eff_ch- x_sto_in[i]/eff_dis )
            model_l.add_constraint(x_sto_wdw[i+1] <= (gen_pv_rate+gen_wind_rate)*sto_time - x_lvl[i] )
            model_l.add_constraint(x_sto_wdw[i+1] <= sto_energy-x_lvl[i])

    # model_l.minimize(sto_energy*(per_cost_sto_energy+om_sto)+gen_wind_rate*(per_cost_wind+om_wind)+gen_pv_rate*(per_cost_pv+om_pv)+sto_charge*(per_cost_sto_charge+om_ch)+sto_dis*(per_cost_sto_dis+om_dis)
                     # (x_sto_in[i]*(sto_in_po) +x_sto_wdw[i]*sto_in_po  for i in range(timeload))
                     # )
    # model_l.minimize((x_sto_in[i]+x_sto_wdw[i])*sto_in_po for i in range(timeload))
    # model_l.minimize(model_l.sum(x_sto_in[i]) for i in range(timeload))


    'inv cost'
    obj =sto_energy*(per_cost_sto_energy+om_sto)+gen_wind_rate*(per_cost_wind+om_wind)+gen_pv_rate*(per_cost_pv+om_pv)+sto_charge*(per_cost_sto_charge+om_ch)+sto_dis*(per_cost_sto_dis+om_dis)
    'opera cost'
    # for i  in range(timeload):
    #     obj2  =(x_sto_in[i]+ x_sto_wdw[i])*sto_in_po+x_fuel_in_sto[i]*res_price[i]+x_fuel_in[i]*res_price[i]

    model_l.minimize(obj)
    # model_l.minimize(obj + obj2)
    solution = model_l.solve()
    return solution





if __name__ == '__main__':
    pd_load, pd_ResGrid_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

    min = min_cost(timeload= 20,gen_pv_max=2000,gen_wind_max=2000,sto_energy_max=5000,sto_charge_max=3000,load=pd_load,
    sto_dis_max=3000,k_down=0.9,k_up=0.9,min_power=0.2,max_power=2,eff_dis=0.9,eff_ch=0.9,max_h=300,min_h=0,per_cost_sto_dis=1000,per_cost_sto_charge=1000,per_cost_sto_energy=1000,per_cost_wind=5000,per_cost_pv=6000,om_wind=100,om_dis=100,om_sto=100,om_ch=100,om_pv=100
             ,res_price=pd_ResGrid_price,sto_in_po=10)

    print(min )


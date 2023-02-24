from docplex.mp import model
from data_load.data_load import data_load



def model_init(gen_num:int,sto_num:int,time_loop:int,load:list,gen_max ,sto_cha_max,sto_energy_max,
              k_up:float,k_down:float,eff_ch:float,eff_dis:float,h_max,h_min,
               cost_per_gen,cost_per_sto,cost_per_sto_ch,cost_per_sto_energy,
               cost_om_gen,cost_om_sto_energy,cost_om_sto_ch,cost_po_gen,cost_po_sto,res_Grid_price,

               ):
    load = load
    '''

    :param gen_num: gen device num
    :param sto_num: sto device num
    :param time_loop: time_loop h
    :return:model
    '''
    '''
    var set
    '''
    model_x =model.Model()
    'cost'
    gen_cap = model_x.continuous_var_list([i for i in range(gen_num)] ,name='gen_cap',lb=0)
    sto_cap = model_x.continuous_var_list([i for i in range(sto_num)],name='sto_cap',lb=0)
    sto_ch = model_x.continuous_var_list([i for  i in range(sto_num)],name='sto_ch',lb=0)
    'cap'
    sto_energy= model_x.continuous_var_list([i for  i in range(sto_num)],name='sto_energy',lb=0)
    'power'
    gen_output=model_x.continuous_var_list([i for i in range(time_loop)], name='gen_output', lb=0)
    sto_inj =model_x.continuous_var_list([i for i in range(time_loop)], name='sto_inj', lb=0)
    sto_wdw = model_x.continuous_var_list([i for i in range(time_loop)], name='sto_wdw', lb=0)
    'sto'
    x_lvl =model_x.continuous_var_list([i for i in range(time_loop)],name='sto_lvl',lb=0)

    sto_time =model_x.continuous_var(lb=h_min,ub=h_max,name='sto_time')
    '''
    cons set 
    '''
    for i  in range(time_loop):
        model_x.add_constraint(gen_output[i]<= gen_max )
        model_x.add_constraint(sto_wdw[i] <=sto_cha_max )
    '''
    fuel cost
    '''
    fuel_inj = model_x.continuous_var_list([i for i in range(time_loop)],name='fuel_inj',lb=0)
    model_x.add_constraint(fuel_inj[i+1]+sto_inj[i+1] <=sto_cap-x_lvl[i] for i in range(time_loop))
    model_x.add_constraint(model_x.sum(fuel_inj[:i])+model_x.sum(sto_inj[:i]) <=sto_cap for i in range(time_loop))







    model_x.add_constraint(x_lvl[i] <= sto_energy_max for i in range(time_loop))


    model_x.add_constraint(gen_output[i] +sto_inj[i] - sto_wdw[i]  ==load[i]  for i in range(time_loop))
    model_x.add_constraint(k_down*(gen_cap+sto_cap)<gen_output[i+1]+sto_inj[i+1] - gen_output[i] - sto_inj[i] <=k_up*(gen_cap+sto_cap)
                           for i in range(time_loop-1)
                           )

    model_x.add_constraint(x_lvl[i+1] - x_lvl[i]  == sto_wdw[i]*eff_ch- sto_inj[i]*eff_dis for i in range(time_loop -1))

    model_x.add_constraint(x_lvl[i] <=sto_time*(gen_cap+sto_cap) for i in range(time_loop))

    model_x.add_constraint(sto_wdw[i+1] <=sto_time*(gen_cap+sto_cap) -x_lvl[i] for i in range(time_loop))

    model_x.add_constraint( gen_cap*h_min <=sto_cap <=gen_cap*h_max)

    model_x.add_constraint(x_lvl[i] <=sto_cap for i in range(time_loop))

    model_x.add_constraint(sto_wdw[i+1] <=sto_cap-x_lvl[i] for i in range(time_loop))

    model_x.add_constraint(sto_wdw[i]<sto_ch for i in range(time_loop))


    'obj'
    model_x.maximize(gen_cap*cost_per_gen+sto_cap*cost_per_sto+sto_ch*cost_per_sto_ch+sto_energy*cost_per_sto_energy
                     +cost_om_sto_ch*sto_ch+cost_om_sto_energy*sto_energy+cost_om_gen*gen_cap+
                     gen_output[i]*cost_po_gen+sto_wdw[i]*cost_po_sto+fuel_inj[i]*res_Grid_price[i]  for i in range(time_loop))



    return model_x
if __name__ == '__main__':
    pd_load, pd_ResGrid_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()




    model_init(gen_num=1,sto_num=1,time_loop=10,load=pd_load,gen_max=5000,sto_cha_max=10000,sto_energy_max=2000,k_down=0.9,k_up=0.9,eff_ch=0.9,eff_dis=0.9,h_max=1000,h_min=0,cost_po_gen=100,cost_po_sto=500,res_Grid_price=pd_ResGrid_price
               ,cost_om_gen=100,cost_per_gen=5000,cost_om_sto_ch=1190,cost_per_sto_energy=1700,cost_om_sto_energy=100,cost_per_sto=1000,cost_per_sto_ch=1190
            )

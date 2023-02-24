from docplex.mp import model



def model_init(gen_num:int,sto_num:int,time_loop:int,load:list,gen_max ,sto_cha_max,sto_energy_max,
              k_up:int,k_down:int,eff_ch:float,eff_dis:float,h_max,h_min,
               cost_per_gen,cost_per_sto,cost_per_sto_ch,cost_per_sto_energy,
               cost_om_gen,cost_om_sto_energy,cost_om_sto_ch,cost_po_gen,cost_po_sto,
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
    model_x.add_constraint(gen_output[i]<= gen_max for i in range(time_loop))
    model_x.add_constraint(sto_wdw[i] <=sto_cha_max for i in range(time_loop))


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
                     gen_output[i]*cost_po_gen+sto_wdw[i]*cost_po_sto  for i in range(time_loop))













    return model_x
if __name__ == '__main__':

    print(model_init(gen_num=2,sto_num=2,time_loop=10))

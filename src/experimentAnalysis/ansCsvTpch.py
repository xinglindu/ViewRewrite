import pandas as pd

eps_list = [0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64]
path = '/8T/xinglin/tpc_h/privacy/experiment/tpch/compare/10M/lineitem/count/'

for i in eps_list:
    data = pd.read_csv(path + 'eps' + str(i) + '/all_ans_eigen.csv')
    median_value = data['relative_error'].median()
    print(round(median_value, 4))

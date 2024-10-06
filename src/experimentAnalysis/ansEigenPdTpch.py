import pickle
import pandas as pd
import matplotlib.pyplot as plt
import math
from collections import OrderedDict


def pd_every_view_ans_eigen_to_csv(ans_eigen_non_negative_path, views_information_path):
    view_ans_pd_dict = get_pd_every_view_ans_eigen(ans_eigen_non_negative_path)
    csv_path = '../../experiment/tpch/every_ans_csv/'
    for key, value in view_ans_pd_dict.items():
        tau, dlsq = get_view_tau_dlsq(views_information_path, key)
        print(key)
        print('dlsq: ', dlsq, 'tau: ', tau, 'median absolute error: ', value['absolute_error'].median(),
              'median relative error: ', value['relative_error'].median())
        print(value)
        value.to_csv(csv_path + str(key)[:250] + '.csv')


def pd_views_query_eigen_to_csv(ans_eigen_non_negative_path, views_information_path):
    view_list = []
    dlsq_list = []
    tau_list = []
    median_absolute_error_list = []
    median_relative_error_list = []
    view_ans_pd_dict = get_pd_every_view_ans_eigen(ans_eigen_non_negative_path)
    csv_path = '../../experiment/tpch/views_query_information.csv'
    for key, value in view_ans_pd_dict.items():
        tau, dlsq = get_view_tau_dlsq(views_information_path, key)
        view_list.append(key)
        dlsq_list.append(dlsq)
        tau_list.append(tau)
        median_absolute_error_list.append(value['absolute_error'].median())
        median_relative_error_list.append(value['relative_error'].median())
    data = pd.DataFrame(
        {'views': view_list, 'dlsq': dlsq_list, 'tau': tau_list, 'median absolute error': median_absolute_error_list,
         'median relative error': median_relative_error_list})
    data.to_csv(csv_path)
    print(len(view_ans_pd_dict))


def plt_every_view_ans_eigen(ans_eigen_non_negative_path, views_information_path):
    view_ans_pd_dict = get_pd_every_view_ans_eigen(ans_eigen_non_negative_path)
    plt.style.use('ggplot')
    b = 1
    a = math.ceil(len(view_ans_pd_dict) / b)
    fig, axs = plt.subplots(a, b, figsize=(100, 90), sharex=False, sharey=False)
    for i, key in enumerate(view_ans_pd_dict):
        plot_comparison_bar_chart(axs[math.floor(i / b)], view_ans_pd_dict[key], key)
    plt.subplots_adjust(wspace=0.3, hspace=0.5)
    plt.tight_layout()
    plt.show()


def plot_comparison_bar_chart(ax, df, title):
    x = range(len(df))
    width = 0.4
    ax.bar(x, df['real_ans'], width=width, label='real_ans')
    ax.bar([pos + width for pos in x], df['privacy_ans'], width=width, label='privacy_ans')

    ax.set_xticks([pos + width / 2 for pos in x])
    ax.set_xticklabels(df.index)
    ax.tick_params(axis='x', rotation=0)  # Rotate x-axis labels

    ax.set_xlabel('index')
    ax.set_ylabel('ans')
    ax.set_title(title)
    ax.legend()


def get_pd_every_view_ans_eigen(path):
    all_ans = read_pickle(path)
    all_ans_pd = pd.DataFrame(all_ans)
    all_ans_pd = all_ans_pd.rename_axis("index")
    all_ans_pd = all_ans_pd.fillna(0)

    all_ans_pd['real_ans'] = all_ans_pd['real_ans'].apply(lambda x: float(x))
    all_ans_pd['privacy_ans'] = all_ans_pd['privacy_ans'].apply(lambda x: float(x))
    all_ans_pd['absolute_error'] = abs(all_ans_pd['real_ans'] - all_ans_pd['privacy_ans'])
    min_denominator = 50
    denominator = all_ans_pd['real_ans'].copy()
    denominator[denominator < min_denominator] = min_denominator
    all_ans_pd['relative_error'] = abs(all_ans_pd['real_ans'] - all_ans_pd['privacy_ans']) / denominator
    all_ans_pd['query'] = all_ans_pd['query'].str.replace('\n', '').str.replace(r'\s+', ' ', regex=True).str.strip()
    view_set = set(list(all_ans_pd['view']))
    view_ans_pd_dict = OrderedDict()
    for i in view_set:
        filter_ans = all_ans_pd[all_ans_pd['view'] == i]
        filter_ans = filter_ans.drop(columns=['view'])
        view_ans_pd_dict[i] = filter_ans
        # print(filter_ans)
    return view_ans_pd_dict


def get_view_tau_dlsq(path, view):
    tau, dlsq = None, None
    view_information = read_pickle(path)
    for i in view_information:
        if ((i[0], i[2]) == view):
            dlsq = i[-2]
            tau = i[-1]
    return tau, dlsq


def pd_all_ans_eigen_to_csv(path):
    all_ans = read_pickle(path)
    all_ans_pd = pd.DataFrame(all_ans)
    all_ans_pd = all_ans_pd.rename_axis("index")
    all_ans_pd = all_ans_pd.fillna(0)
    all_ans_pd['real_ans'] = all_ans_pd['real_ans'].apply(lambda x: float(x))
    all_ans_pd['privacy_ans'] = all_ans_pd['privacy_ans'].apply(lambda x: float(x))
    all_ans_pd['absolute_error'] = abs(all_ans_pd['real_ans'] - all_ans_pd['privacy_ans'])
    min_denominator = 50
    denominator = all_ans_pd['real_ans'].copy()
    denominator[denominator < min_denominator] = min_denominator
    all_ans_pd['relative_error'] = abs(all_ans_pd['real_ans'] - all_ans_pd['privacy_ans']) / denominator
    all_ans_pd.to_csv('../../experiment/tpch/all_ans_eigen.csv')
    print('all absolute error', all_ans_pd['absolute_error'].median())
    print('all relative error', all_ans_pd['relative_error'].median())


def read_pickle(path):
    with open(path, 'rb') as file:
        loaded_data = pickle.load(file)
    return loaded_data


if __name__ == "__main__":
    ans_eigen_path = '../../experiment/tpch/ans_eigen_pd.pkl'
    ans_eigen_non_negative_path = '../../experiment/tpch/ans_eigen_non_negative_pd.pkl'
    views_information_path = '../../views/tpch/views_information.pkl'
    pd_every_view_ans_eigen_to_csv(ans_eigen_non_negative_path, views_information_path)
    pd_all_ans_eigen_to_csv(ans_eigen_non_negative_path)
    pd_views_query_eigen_to_csv(ans_eigen_non_negative_path, views_information_path)
    # plt_every_view_ans_eigen(ans_eigen_non_negative_path,views_information_path)

import sys

sys.path.append('../dataProtection/')
from viewGenerate import view_generate_main as view_generate
from controlConvert import access_get_orig


def file_generate_view(pass_queries_path):
    view_attr_set_list, view_primary_sub_all_list, view_primary_no_sub_all_list = view_generate(pass_queries_path)
    view_primary_sub_re = []
    view_primary_no_sub_re = []
    orig_query_primary_no_sub, orig_query_primary_sub = access_get_orig(pass_queries_path[0])
    if len(view_primary_no_sub_all_list) > 0:
        for i in view_primary_no_sub_all_list:
            view_primary_no_sub_re.append([(str(i[0]), str(i[1])), str(i[2])])
    if len(view_primary_sub_all_list) > 0:
        for i in view_primary_sub_all_list:
            tmp = []
            for j in i:
                tmp.append([(str(j[0]), str(j[1])), str(j[2])])
            view_primary_sub_re.append(tmp)
    # for i,tt in enumerate(view_primary_sub_re):
    #     print(tt,orig_query_primary_sub[i])
    # for i,tt in enumerate(view_primary_no_sub_re):
    #     print(tt,orig_query_primary_no_sub[i])

    return view_primary_sub_re, orig_query_primary_sub, view_primary_no_sub_re, orig_query_primary_no_sub


if __name__ == "__main__":
    pass_queries_path = ['../../dataQuery/tpch/query/pass_analysis_queries.sql']
    file_generate_view(pass_queries_path)

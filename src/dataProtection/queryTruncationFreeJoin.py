# -*- coding: utf-8 -*-
import getopt
import math
import sys
import random
import time


def ReadInput():
    global input_file_path
    global size_dic
    global real_query_result
    real_query_result = 0
    size_dic = {}
    input_file = open(input_file_path, 'r')
    for line in input_file.readlines():
        elements = line.split()
        value = float(elements[0])
        entity = int(elements[1])
        real_query_result += value
        if entity in size_dic.keys():
            size_dic[entity] += value
        else:
            size_dic[entity] = value


def query_LP_truncation_free_join():
    global size_dic
    global truncation_query_result
    res = 0
    for element in size_dic.keys():
        res += min(tau, size_dic[element])
    truncation_query_result = res


def main_query_LP_truncation_free_join(argv):
    # The input file including the relationships between aggregations and base tuples
    global input_file_path
    input_file_path = ""
    global tau
    global real_query_result
    global truncation_query_result
    try:
        opts, args = getopt.getopt(argv, "h:I:T:", ["Input=", "tau="])
    except getopt.GetoptError:
        print("queryTruncationFreeJoin.py -I <input file> -T <tau>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("queryTruncationFreeJoin.py -I <input file> -T <tau>")
            sys.exit()
        elif opt in ("-I", "--Input"):
            input_file_path = str(arg)
        elif opt in ("-T", "--tau"):
            tau = arg
    ReadInput()
    query_LP_truncation_free_join()
    # print("Real Query Result",real_query_result)
    return truncation_query_result


if __name__ == "__main__":
    main_query_LP_truncation_free_join(['-I', 'out.txt', '-T', 9])

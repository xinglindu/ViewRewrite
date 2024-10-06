# -*- coding: utf-8 -*-
import getopt
import math
import sys
import random
import cplex
import numpy as np
import time
import gc
import multiprocessing
from multiprocessing.sharedctypes import Value
from ctypes import c_double

manager = multiprocessing.Manager()
gc.enable()


def compute_query_dlsq():
    global input_file_path
    # Store the ids of entities
    global entities
    # The connections between entities and join results
    global connections
    # The DS
    global downward_sensitivity
    # The aggregation values of join results
    global aggregation_values
    # The real query result
    global real_query_result
    # The dictionary to store the tuples' sensitivities
    entities_sensitivity_dic = {}
    # The dictionary to re-id entities
    id_dic = {}
    # The number of base table tuples
    id_num = 0
    # Collect the DS
    downward_sensitivity = 0
    # The variable is repsented one entity
    entities = []
    connections = []
    aggregation_values = []
    input_file = open(input_file_path, 'r')
    for line in input_file.readlines():
        elements = line.split()
        connection = []
        # The first value is the aggregation value
        aggregation_value = float(elements[0])
        # For each entity contribution to that join result
        for element in elements[1:]:
            element = int(element)
            # Re-order the IDs
            if element in id_dic.keys():
                element = id_dic[element]
            else:
                entities.append(id_num)
                id_dic[element] = id_num
                element = id_num
                id_num += 1
            # Update the entity's sensitivity
            if element in entities_sensitivity_dic.keys():
                entities_sensitivity_dic[element] += aggregation_value
            else:
                entities_sensitivity_dic[element] = aggregation_value
            # Update the DS
            if downward_sensitivity <= entities_sensitivity_dic[element]:
                downward_sensitivity = entities_sensitivity_dic[element];
            connection.append(element)
        connections.append(connection)
        aggregation_values.append(aggregation_value)
    real_query_result = sum(aggregation_values)
    return downward_sensitivity


def main_compute_query_dlsq(argv):
    # The input file including the relationships between aggregations and base tuples
    global input_file_path
    input_file_path = ""
    try:
        opts, args = getopt.getopt(argv, "h:I:", ["Input="])
    except getopt.GetoptError:
        print("computeQueryDlsq.py -I <input file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("computeQueryDlsq.py -I <input file>")
            sys.exit()
        elif opt in ("-I", "--Input"):
            input_file_path = str(arg)
    # Two processors for one task: primal and dual
    return compute_query_dlsq()


if __name__ == "__main__":
    # main(sys.argv[1:])
    main_compute_query_dlsq(['-I', 'out.txt'])

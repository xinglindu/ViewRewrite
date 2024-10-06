import sqlparse
import sys

sys.path.append('../queryAnalysis/')
from setupAnalysis import setupQueryAnalysis

color_code = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m'
}


def file_analysis(filename):
    pass_query_list = []
    with open(filename, "r") as f:
        queries = f.read()
        format_queries = sqlparse.format(queries, keyword_case="upper", identifier_case="lower", strip_comments=True,
                                         use_space_around_operators=True)
    format_query_list = format_queries.split("\n")
    for query in format_query_list:
        if len(query) > 0:
            fieldReviewResult = setupQueryAnalysis(query)
            if "error" in fieldReviewResult:
                print(color_code['red'] + query, fieldReviewResult, color_code['reset'])
            else:
                pass_query_list.append(query)
                print(fieldReviewResult)
    return pass_query_list


def file_analysis_fake(filename):
    with open(filename, "r") as f:
        queries = f.read()
        format_queries = sqlparse.format(queries, keyword_case="upper", identifier_case="lower", strip_comments=True,
                                         use_space_around_operators=True)
    format_query_list = format_queries.split("\n")
    return format_query_list


def files_analysis(filename_list, pass_queries_path):
    pass_query_list = []
    for filename in filename_list:
        pass_query_list.extend(file_analysis_fake(filename))
    write_sql_to_file(pass_query_list, pass_queries_path)


def write_sql_to_file(sql_list, file_path):
    with open(file_path, 'w') as file:
        for sql_statement in sql_list:
            file.write(sql_statement)
            file.write('\n')


if __name__ == "__main__":
    list_filename = ["../../dataQuery/tpch/query/original_query/all/count.sql",
                     "../../dataQuery/tpch/query/original_query/all/sum.sql"]
    pass_queries_path = '../../dataQuery/tpch/query/pass_analysis_queries.sql'
    files_analysis(list_filename, pass_queries_path)

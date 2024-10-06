import sys

sys.path.append('../')
from setupAnalysis import setupQueryAnalysis


def test_main(filename):
    with open(filename, "r") as f:
        queries = f.read()
        query_list = queries.split("\n")
        for query in query_list:
            if (len(query) > 0):
                fieldReviewResult = setupQueryAnalysis(query)
                print(fieldReviewResult)


if __name__ == "__main__":
    test_main("../../../dataQuery/tpch/query/original_query/base/count.sql")
    test_main("../../../dataQuery/tpch/query/original_query/base/sum.sql")

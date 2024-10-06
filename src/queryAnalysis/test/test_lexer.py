import sys

sys.path.append('../')
from setupAnalysis import setupQueryAnalysis

if __name__ == "__main__":
    sql = "SELECT COUNT(*) FROM sc WHERE sno=1/* note */;"
    fieldReviewResult = setupQueryAnalysis(sql)
    print("\n", sql, "\n", fieldReviewResult, "\n")

    sql = "SELECT COUNT(*) FROM        sc WHERE sno=1;"
    fieldReviewResult = setupQueryAnalysis(sql)
    print("\n", sql, "\n", fieldReviewResult, "\n")

    sql = "select count(*) from Sc where sno=1;"
    fieldReviewResult = setupQueryAnalysis(sql)
    print("\n", sql, "\n", fieldReviewResult, "\n")

    sql = "select count(*) fro sc where sno=1;"
    fieldReviewResult = setupQueryAnalysis(sql)
    print("\n", sql, "\n", fieldReviewResult, "\n")

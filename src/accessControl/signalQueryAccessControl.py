import sys

sys.path.append('../queryAnalysis/')
from mainAnalysis import mainQueryAnalysis as queryAnalysis

if __name__ == "__main__":
    sql = ""
    fieldReviewResult = queryAnalysis(sql)
    if "error" in fieldReviewResult:
        print(fieldReviewResult)
    else:
        pass

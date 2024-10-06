from lexerAnalysis import lexerCheck
from syntaxAnalysis import syntaxCheck
from semanticAnalysis import semanticCheck


def mainQueryAnalysis(query):  #
    rawQuery = query
    lexerResult = lexerCheck(query)
    if lexerResult == "Lexical error!":
        return lexerResult
    else:
        syntaxResult = syntaxCheck(lexerResult)
        if "error" in syntaxResult:
            return syntaxResult
        else:
            semanticResult = semanticCheck(syntaxResult, rawQuery)
            return semanticResult


if __name__ == "__main__":
    sql = ''
    fieldReviewResult = mainQueryAnalysis(sql)
    if "error" in fieldReviewResult:
        print(fieldReviewResult)
    else:
        print(fieldReviewResult)

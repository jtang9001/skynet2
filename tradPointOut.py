from peewee import *
from tabulabuilder import School, Swimmer, Result, RelayResult
import numpy as np

def rankToPoints2017(rank):
    try:
        if np.isnan(rank):
            return 0
        if rank <= 5:
            return 22 - rank * 2
        else:
            return max(17 - 1 * rank, 0)
    except TypeError:
        #print("Comparison cannot be made for {}, returning 0".format(rank))
        return 0

def rankToPoints2016(rank):
    try:
        if rank <= 2:
            return 24 - 2 * rank
        elif 2 < rank <= 8:
            return 22 - rank * 1
        else:
            return 0
    except TypeError:
        print("Comparison cannot be made for {}, returning 0".format(rank))
        return 0

def rankToPoints(rank, year):
    if year == 2016:
        return rankToPoints2016(rank)
    else:
        return rankToPoints2017(rank)


def getIndsForSchool(school: School, year: int):
    return Result.select().where(
        (Result.school == school) 
        & (Result.year == year) 
        & (Result.divsRank.is_null(False))
        & (Result.qualified == True)
    )

def getRelaysForSchool(school: School, year: int):
    return RelayResult.select().where(
        (RelayResult.school == school) 
        & (RelayResult.year == year)
        & (RelayResult.divsRank.is_null(False))
        & (RelayResult.qualified == True)
    )

if __name__ == "__main__":
    YEAR = 2019

    points = {}

    # db = SqliteDatabase("results.db", pragmas = {
    #     'foreign_keys': 1,
    #     'ignore_check_constraints': 0}
    # )

    # db.connect()

    for school in School.select():
        points[school.name] = sum([rankToPoints(result.divsRank, YEAR) for result in getIndsForSchool(school, YEAR)])
        points[school.name] += sum([rankToPoints(result.divsRank, YEAR) for result in getRelaysForSchool(school, YEAR)])

    for school, pts in sorted(points.items(), key = lambda x: x[1], reverse=True):
        print(school, pts)

    # db.close()
from peewee import *
from tabulabuilder import School, Swimmer, Result, RelayResult

def rankToPoints2017(rank):
    try:
        if rank <= 5:
            return 22 - rank * 2
        else:
            return max(17 - 1 * rank, 0)
    except TypeError:
        print("Comparison cannot be made for {}, returning 0".format(rank))
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
        & (Result.finalRank.is_null(False)))

def getRelaysForSchool(school: School, year: int):
    return RelayResult.select().where(
        (RelayResult.school == school) 
        & (RelayResult.year == year)
        & (RelayResult.finalRank.is_null(False)))

if __name__ == "__main__":
    YEAR = 2017

    points = {}

    for school in School.select():
        points[school.name] = sum([rankToPoints(result.finalRank, YEAR) for result in getIndsForSchool(school, YEAR)])
        points[school.name] += sum([rankToPoints(result.finalRank, YEAR) for result in getRelaysForSchool(school, YEAR)])

    for school, pts in sorted(points.items(), key = lambda x: x[1], reverse=True):
        print(school, pts)
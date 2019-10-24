from peewee import *
from tabulabuilder import School, Swimmer, Result, RelayResult

def rankToPoints(rank):
    try:
        if rank <= 5:
            return 22 - rank * 2
        else:
            return max(17 - 1 * rank, 0)
    except TypeError:
        print("Comparison cannot be made for {}, returning 0".format(rank))
        return 0

def getIndsForSchool(school: School, year: int):
    return Result.select().join(Swimmer).join(School).where(
        (Swimmer.school == school) 
        & (Result.year == year) 
        & (Result.finalRank.is_null(False)))

def getRelaysForSchool(school: School, year: int):
    return RelayResult.select().where(
        (RelayResult.school == school) 
        & (RelayResult.year == YEAR)
        & (RelayResult.finalRank.is_null(False)))

YEAR = 2017

points = {}

for school in School.select():
    points[school.name] = sum([rankToPoints(result.finalRank) for result in getIndsForSchool(school, YEAR)])
    points[school.name] += sum([rankToPoints(result.finalRank) for result in getRelaysForSchool(school, YEAR)])

for school, pts in sorted(points.items(), key = lambda x: x[1], reverse=True):
    print(school, pts)
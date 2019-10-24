from peewee import *
from tabulabuilder import School, Swimmer, RelayResult, Result
from tradPointOut import getRelaysForSchool, getIndsForSchool, rankToPoints

sch = School.get_by_id(29)

for result in getIndsForSchool(sch, 2016):
    print(rankToPoints(result.finalRank), result)
from peewee import *
from tabulanet import School, Swimmer

def mergeSchools(fromname, toname):
    fromSchool = School.get(name = fromname)
    toSchool = School.get(name = toname)

    

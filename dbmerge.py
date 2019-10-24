from peewee import *
from tabulabuilder import School, Swimmer, RelayResult

def mergeSchools(fromSchool, toSchool):
    # fromSchool = School.get(name = fromname)
    # toSchool = School.get(name = toname)

    query = Swimmer.update(school = toSchool).where(Swimmer.school == fromSchool)
    numSwimmersChanged = query.execute()

    query = RelayResult.update(school = toSchool).where(RelayResult.school == fromSchool)
    numRelaysChanged = query.execute()
    
    fromSchool.delete_instance()
    print("{} entries changed".format(numSwimmersChanged + numRelaysChanged))

def mergeSchoolsByID(fromID, toID):
    fromSchool = School.get_by_id(fromID)
    toSchool = School.get_by_id(toID)

    print(fromSchool.name, toSchool.name)

    mergeSchools(fromSchool, toSchool)


if __name__ == "__main__":
    mergeSchoolsByID(24, 33)
    # for fromSchool in School.select():
    #     if "School" in fromSchool.name:
    #         try:
    #             toSchoolName = fromSchool.name.replace(" School", "")
    #             toSchool = School.get(name = toSchoolName)
    #             print(fromSchool.name, toSchoolName)

    #             mergeSchools(fromSchool, toSchool)
    #         except DoesNotExist:
    #             print("No matching shorter name for {}".format(fromSchool.name))
from peewee import *
from tabulabuilder import School, Result, RelayResult

def cleanName(name):
    name = name.replace("High", "")
    name = name.replace("School", "")
    name = "".join(char.lower() for char in name if char.isalpha())
    return name


def mergeSchools(fromSchool, toSchool):
    # fromSchool = School.get(name = fromname)
    # toSchool = School.get(name = toname)

    query = Result.update(school = toSchool).where(Result.school == fromSchool)
    numResultsChanged = query.execute()

    query = RelayResult.update(school = toSchool).where(RelayResult.school == fromSchool)
    numRelaysChanged = query.execute()
    
    fromSchool.delete_instance()
    print("{} entries changed".format(numResultsChanged + numRelaysChanged))

def mergeSchoolsByID(fromID, toID):
    fromSchool = School.get_by_id(fromID)
    toSchool = School.get_by_id(toID)

    print(fromSchool.name, toSchool.name)

    mergeSchools(fromSchool, toSchool)

def getMatchingSchools():
    schools = list(School.select())

    for i in range(len(schools)):
        for j in range(i + 1, len(schools)):
            if cleanName(schools[i].name) == cleanName(schools[j].name):
                if len(schools[i].name) < len(schools[j].name):
                    return schools[j], schools[i]
                else:
                    return schools[i], schools[j]

    return None, None



if __name__ == "__main__":
    #mergeSchoolsByID(24, 33)
    # for fromSchool in School.select():
    #     if "School" in fromSchool.name:
    #         try:
    #             toSchoolName = fromSchool.name.replace(" School", "")
    #             toSchool = School.get(name = toSchoolName)
    #             print(fromSchool.name, toSchoolName)

    #             mergeSchools(fromSchool, toSchool)
    #         except DoesNotExist:
    #             print("No matching shorter name for {}".format(fromSchool.name))
    
    while True:
        sch1, sch2 = getMatchingSchools()
        if sch1 is None:
            break
        print(sch1.name, sch2.name)
        mergeSchools(sch1, sch2)
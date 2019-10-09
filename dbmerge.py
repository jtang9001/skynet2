from peewee import *
from tabulanet import School, Swimmer

def mergeSchools(fromSchool, toSchool):
    # fromSchool = School.get(name = fromname)
    # toSchool = School.get(name = toname)

    query = Swimmer.update(school = toSchool).where(Swimmer.school == fromSchool)
    numRowsChanged = query.execute()
    
    fromSchool.delete_instance()
    print("{} entries changed".format(numRowsChanged))

if __name__ == "__main__":
    for fromSchool in School.select():
        if "High School" in fromSchool.name:
            try:
                toSchoolName = fromSchool.name.replace(" High School", "")
                toSchool = School.get(name = toSchoolName)
                print(fromSchool.name, toSchoolName)

                mergeSchools(fromSchool, toSchool)
            except DoesNotExist:
                print("No matching shorter name for {}".format(fromSchool.name))
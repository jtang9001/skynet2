import pandas as pd
from tabulabuilder import Swimmer, Result
from playhouse.shortcuts import model_to_dict

attendanceDf = pd.read_csv("attendance.csv")

def getAttendanceForSwimmer(swimmer: Swimmer):
    return attendanceDf.loc[attendanceDf["Name"] == str(swimmer)].iat[0,1]

sconaResults = Result.select().where((Result.school == 1) & (Result.year == 2019)).objects()

dfSource = []

for result in sconaResults:

    rd = model_to_dict(result, recurse=False)

    for virtFieldName in result.virtFields:
        if hasattr(result, virtFieldName):
            rd[virtFieldName] = getattr(result, virtFieldName)()

    rd["attendance"] = getAttendanceForSwimmer(result.swimmer)
    rd["eventName"] = str(result.event)

    dfSource.append(rd)

resultsDf = pd.DataFrame(dfSource)

resultsDf["seedToDivsTimeDelta"] = resultsDf["divsTime"] - resultsDf["seedTime"]
resultsDf["divsToCitiesTimeDelta"] = resultsDf["finalTime"] - resultsDf["divsTime"]
resultsDf["seedToCitiesTimeDelta"] = resultsDf["finalTime"] - resultsDf["seedTime"]

resultsDf["seedToDivsSpeedDelta"] = resultsDf["divsSpeed"] - resultsDf["seedSpeed"]
resultsDf["divsToCitiesSpeedDelta"] = resultsDf["finalSpeed"] - resultsDf["divsSpeed"]
resultsDf["seedToCitiesSpeedDelta"] = resultsDf["finalSpeed"] - resultsDf["seedSpeed"]

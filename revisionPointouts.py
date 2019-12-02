from tabulabuilder import Swimmer, Event, Result, School
from playhouse.shortcuts import model_to_dict
from collections import defaultdict
import pandas as pd

YEAR = 2019

skip = [
    {"firstName": "Emma", "lastName": "O'Croinin"}, # ID 1212
    {"firstName": "Sydney", "lastName": "Monilaws"} # ID 1248
]

def getResultsForName(**namekws):
    return [result for result in Swimmer.get_or_none(**namekws).results.objects() if result.year == YEAR]

def getUnqualifiedForEvent(event):
    unQls = sorted(
        event.results.where(
            ~(Result.qualified) 
            & (Result.year == YEAR) 
            & (Result.divsRank.is_null(False))
        ).objects(),
        key = lambda result: result.divsTime
    )

    return [model_to_dict(unQl, recurse=False) for unQl in unQls]


def removePersonFromEvent(event, person, year = YEAR):
    try:
        replResult = event.results.where((Result.swimmer == person) & (Result.year == year)).objects()[0]
        rank = replResult.divsRank
        if not replResult.qualified:
            print("Person is not qualified in this event.")
            return None
        else:
            replResult.qualified = False
            replResult.divsRank = None
            replResult.save()

    except IndexError:
        print("Probably can't find this swimmer in this event!")
        return None

    for result in event.results.where((Result.divsRank.is_null(False)) & (Result.year == year)):
        if result.divsRank > rank:
            result.divsRank -= 1
            result.save()
    
    try:
        newQl = min(event.results.where(
            (~(Result.qualified)) & (Result.divsRank.is_null(False)) & (Result.year == year)
            ), key = lambda result: result.divsTime)
        newQl.qualified = True
        newQl.save()
    except ValueError:
        print("No more people to promote after removing this swimmer")

def getFirstUnqualified(event, n):
    '''
    Returns the first n unqualified people with a divsTime in event.
    '''
    return getUnqualifiedForEvent(event)[:n]

def getSwimmerForName(nameStr):
    names = nameStr.split(", ")
    lastName = names[0]
    firstName = names[1]
    return Swimmer.get(firstName = firstName, lastName = lastName)

def addUnqlEvent(swimmerName, eventName, eventUnqlDict):
    swimmer = getSwimmerForName(swimmerName)
    eventWords = eventName.split()
    dist = int(eventWords[0])
    stroke = eventWords[1]

    events = Event.select().where(
        (Event.distance == dist)
        & (Event.stroke == stroke)
        & (~(Event.isRelay))
        & (Event.gender == swimmer.gender)
    )

    for event in events:
        for result in event.results.where((Result.year == YEAR) & (Result.qualified)):
            if result.swimmer == swimmer:
                eventUnqlDict[event] += 1
                print(f"{swimmer};{event};{result.school}")
                removePersonFromEvent(event, swimmer)
                return


if __name__ == "__main__":
    eventUnqlCount = defaultdict(int)
    reportDf = pd.DataFrame()

    noshow = pd.read_csv("suspnames.csv")
    nominis = pd.read_csv("nominimeets.csv")

    for name in noshow[noshow["MinisName"].isnull()].DivsName:
        swimmer = getSwimmerForName(name)
        for result in swimmer.results.where((Result.year == YEAR) & (Result.qualified)).objects():
            eventUnqlCount[result.event] += 1
            print(f"{swimmer};{result.event};{result.school}")
            removePersonFromEvent(result.event, swimmer)

    nominis.apply(lambda row: addUnqlEvent(row["DivsName"], row["Event"], eventUnqlCount), axis = 1)
    
    for event, numUnql in eventUnqlCount.items():
        newDf = pd.DataFrame(getFirstUnqualified(event, numUnql))
        newDf["event"] = str(event)
        reportDf = pd.concat([reportDf, newDf])
    
    reportDf["school"] = reportDf["school"].apply(lambda sch: School.get_by_id(int(sch)).name)
    reportDf["swimmer"] = reportDf["swimmer"].apply(lambda sch: Swimmer.get_by_id(int(sch)))
    
    print(reportDf)
    #reportDf.to_csv("bumped.csv")





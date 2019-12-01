from tabulabuilder import Swimmer, Event, Result

YEAR = 2019

skip = [
    {"firstName": "Emma", "lastName": "O'Croinin"}, # ID 1212
    {"firstName": "Sydney", "lastName": "Monilaws"} # ID 1248
]

def getResultsForName(**namekws):
    return [result for result in Swimmer.get_or_none(**namekws).results.objects() if result.year == YEAR]

def removePersonFromEvent(event, person, year = YEAR):
    try:
        replResult = event.results.where(Result.swimmer == person).objects()[0]
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

if __name__ == "__main__":
    for person in skip:
        for result in getResultsForName(**person):
            print(result.event)
            removePersonFromEvent(result.event, result.swimmer)


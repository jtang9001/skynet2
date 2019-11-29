from tabulabuilder import Swimmer, Event, Result

YEAR = 2019

skip = [
    {"firstName": "Emma", "lastName": "O'Croinin"},
    {"firstName": "Sydney", "lastName": "Monilaws"}
]

def getResultsForName(**namekws):
    return [result for result in Swimmer.get_or_none(**namekws).results.objects() if result.year == YEAR]



if __name__ == "__main__":
    for person in skip:
        for result in getResultsForName(**person):
            print(result.event)


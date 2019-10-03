from peewee import *
import re

YEAR = 2017

db = SqliteDatabase("results.db", pragmas = {
    'foreign_keys': 1,
    'ignore_check_constraints': 0})

class School(Model):
    name = CharField()

    class Meta:
        database = db

class Swimmer(Model):
    firstName = CharField()
    lastName = CharField()
    gender = CharField()
    school = ForeignKeyField(School, backref = "swimmers")

    class Meta:
        database = db

class Event(Model):
    age = IntegerField(null=True)
    distance = IntegerField()
    stroke = CharField()
    gender = CharField()
    year = IntegerField()
    isRelay = BooleanField()

    class Meta:
        database = db

class Result(Model):
    divsRank = IntegerField(null=True)
    finalRank = IntegerField(null=True)
    swimmer = ForeignKeyField(Swimmer, backref = "results")
    swimmerage = IntegerField(null=True)
    event = ForeignKeyField(Event, backref = "results")
    seedTime = FloatField(null=True)
    divsTime = FloatField(null=True)
    finalTime = FloatField(null=True)
    qualified = BooleanField()

    class Meta:
        database = db

class RelayResult(Model):
    divsRank = IntegerField(null=True)
    finalRank = IntegerField(null=True)
    event = ForeignKeyField(Event, backref = "results")
    seedTime = FloatField(null=True)
    divsTime = FloatField(null=True)
    finalTime = FloatField(null=True)
    qualified = BooleanField()

    class Meta:
        database = db

class RelayParticipant(Model):
    swimmer = ForeignKeyField(Swimmer, backref = "relays")
    relay = ForeignKeyField(RelayResult, backref = "participants")

    class Meta:
        database = db

divsRegexPatterns = {
    2016: re.compile(
        r"""(?P<rank>\d+)[., ]+ #rank, followed by usually a space but also period or comma due to OCR noise
        (?P<firstName>[A-Za-z \-']+),\ (?P<lastName>[A-Za-z \-']+)\ #last name, first name; spaces are escaped due to re.VERBOSE
        (?P<age>[\d.]+)\ #age; space escaped
        (?P<school>[A-Za-z \-'()\d.]+)\ #school name
        (?P<seedTime>(\d+:)?\d{2}\.\d{2}|NT)\ #seed time
        (?P<divsTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,}) #divs time
        [ .]*(?P<qualified>[a-z]*) #qualified indicator, possibly with some OCR noise""",
        re.VERBOSE)
}

divsEventRegexPatterns = {
    2016: re.compile(
        r'''Event\ \d+\ 
        (?P<gender>Boys|Girls|Mixed)\ 
        (?P<age>\d{2}|Open).+
        (?P<distance>50|100|200|400).+Meter\ 
        (?P<stroke>[A-Za-z]+)
        (?P<relay>\ Relay)?''',
        re.VERBOSE)
}

def strToTime(s: str) -> float:
    if ":" in s:
        t = s.split(":")
        return int(t[0]) * 60 + float(t[1])
    else:
        try:
            assert 0 < float(s) < 60
            return float(s)
        except (AssertionError, ValueError):
            print("StrToTime Warning: no time for value", s)
            return None

def noisyInt(s: str) -> int:
    s = ''.join(char for char in s if char.isdigit())
    return int(s)


with open("{} divs.txt".format(YEAR), "r") as f:
    for line in f.readlines():
        if "Event" in line:
            print(line)


# db.connect()
# db.create_tables([School, Swimmer, Event, Result, RelayResult, RelayParticipant])

# with open("{} divs.txt".format(YEAR), "r") as f:
#     currentEvent = None
#     for line in f.readlines():
#         matchResult = divsRegexPatterns[YEAR].search(line)
#         matchEvent = divsEventRegexPatterns[YEAR].search(line)
#         if matchEvent:
#             matchDict = matchEvent.groupdict()
#             print(matchDict)
#             currentEvent = Event.get_or_create(
#                 gender = matchDict["gender"],
#                 stroke = matchDict["stroke"],
#                 year = YEAR,
#                 isRelay = False if matchDict["relay"] is None else True,
#                 age = noisyInt(matchDict["age"]) if matchDict["age"].isdecimal() else None,
#                 distance = noisyInt(matchDict["distance"])
#             )[0]
#         elif matchResult:
#             matchDict = matchResult.groupdict()
#             print(matchDict)
#             school = School.get_or_create(name = matchDict["school"])[0]
#             swimmer = Swimmer.get_or_create(
#                 firstName = matchDict["firstName"],
#                 lastName = matchDict["lastName"],
#                 defaults = {
#                     "gender": currentEvent.gender,
#                     "school": school
#                 }
#             )[0]
#             result = Result.get_or_create(
#                 divsRank = noisyInt(matchDict["rank"]),
#                 swimmer = swimmer,
#                 swimmerage = noisyInt(matchDict["age"]),
#                 event = currentEvent,
#                 qualified = matchDict["qualified"] is not None and 'q' in matchDict["qualified"],
#                 seedTime = strToTime(matchDict["seedTime"]),
#                 divsTime = strToTime(matchDict["divsTime"]),
#             )[0]

# db.close()
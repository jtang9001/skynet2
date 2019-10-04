from peewee import *
import re

YEAR = 2018

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
    year = IntegerField()

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
    year = IntegerField()

    class Meta:
        database = db

class RelayParticipant(Model):
    swimmer = ForeignKeyField(Swimmer, backref = "relays")
    relay = ForeignKeyField(RelayResult, backref = "participants")
    age = IntegerField(null=True)

    class Meta:
        database = db

divsRegexPatterns = {
    2016: re.compile(
        r"""(?P<rank>\d+)[., ]+ #rank, followed by usually a space but also period or comma due to OCR noise
        (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ #last name, first name; spaces are escaped due to re.VERBOSE
        (?P<age>[\d.]+)\ #age; space escaped
        (?P<school>[A-Za-z \-'()\d.]+)\ #school name
        (?P<seedTime>(\d+:)?\d{2}\.\d{2}|NT)\ #seed time
        (?P<divsTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,}) #divs time
        [ .]*(?P<qualified>[a-z]*) #qualified indicator, possibly with some OCR noise""",
        re.VERBOSE),
    2017: re.compile(
        r"""(?P<rank>\d+)[., ]+ #rank, followed by usually a space but also period or comma due to OCR noise
        (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ #last name, first name; spaces are escaped due to re.VERBOSE
        (?P<age>[\d.]+)\ #age; space escaped
        (?P<school>[A-Za-z \-'()\d.]+)\ #school name
        (?P<seedTime>(\d+:)?\d{2}\.\d{2}|NT)\ #seed time
        (?P<divsTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,}) #divs time
        [ .]*(?P<qualified>[a-z]*) #qualified indicator, possibly with some OCR noise""",
        re.VERBOSE),
    2018: re.compile(
        r"""(?P<rank>\d+)[., ]+ #rank, followed by usually a space but also period or comma due to OCR noise
        (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ #last name, first name; spaces are escaped due to re.VERBOSE
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
        re.VERBOSE),
    2017: re.compile(
        r'''Event\ \d+\ 
        (?P<gender>Boys|Girls|Mixed)\ 
        (?P<age>\d{2}|Open).+
        (?P<distance>50|100|200|400).+Meter\ 
        (?P<stroke>[A-Za-z]+)
        (?P<relay>\ Relay)?''',
        re.VERBOSE),
    2018: re.compile(
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
            s = float(s)
            if 1000 <= s < 10000:
                s /= 100
            assert 0 < s < 60
            return s
        except (AssertionError, ValueError):
            print("StrToTime Warning: no time for value", s)
            return None

def noisyInt(s: str) -> int:
    s = ''.join(char for char in s if char.isdigit())
    return int(s)

def ageMatch(age: int) -> int:
    ageMap = {
        10: 15,
        11: 16,
        20: 16,
        21: 17,
        30: 17,
    }

    if age in ageMap:
        return ageMap[age]
    else:
        return age


# with open("{} divs.txt".format(YEAR), "r") as f:
#     for line in f.readlines():
#         if "Event" in line:
#             print(line)


db.connect()
db.create_tables([School, Swimmer, Event, Result, RelayResult, RelayParticipant])

with open("{} divs.txt".format(YEAR), "r") as f:
    currentEvent = None
    for line in f.readlines():
        print(line.strip())
        matchResult = divsRegexPatterns[YEAR].search(line)
        matchEvent = divsEventRegexPatterns[YEAR].search(line)
        if matchEvent:
            if "Swim-off" in line:
                currentEvent = None
                continue
            matchDict = matchEvent.groupdict()
            print(matchDict)
            currentEvent = Event.get_or_create(
                gender = matchDict["gender"],
                stroke = matchDict["stroke"],
                isRelay = False if matchDict["relay"] is None else True,
                age = ageMatch(noisyInt(matchDict["age"])) if matchDict["age"].isdecimal() else None,
                distance = noisyInt(matchDict["distance"])
            )
        elif matchResult and currentEvent is not None:
            matchDict = matchResult.groupdict()
            print(matchDict)
            school = School.get_or_create(name = matchDict["school"])
            swimmer = Swimmer.get_or_create(
                firstName = matchDict["firstName"],
                lastName = matchDict["lastName"],
                defaults = {
                    "gender": currentEvent[0].gender,
                    "school": school[0]
                }
            )
            result = Result.get_or_create(
                divsRank = noisyInt(matchDict["rank"]),
                swimmer = swimmer[0],
                event = currentEvent[0],
                seedTime = strToTime(matchDict["seedTime"]),
                divsTime = strToTime(matchDict["divsTime"]),
                year = YEAR,
                defaults = {
                    "swimmerage": ageMatch(noisyInt(matchDict["age"])),
                    "qualified": matchDict["qualified"] is not None and 'q' in matchDict["qualified"]
                }
            )

db.close()
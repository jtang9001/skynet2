import pandas as pd
import numpy as np
import tabula
import PyPDF2
import re
import traceback
import types
from peewee import *

regexes = {
    "event": re.compile(
        r'''Event\ \d+\ +
        (?P<gender>Boys|Girls|Mixed)\ 
        (?P<age>\d{2}|Open).+
        (?P<distance>50|100|200|400).+Meter\ 
        (?P<stroke>[A-Za-z]+)
        (?P<relay>\ Relay)?''',
        re.VERBOSE),

    "divsInd": re.compile(
        r"""(?P<rank>[\-\d]+)(.0)?\ + #rank, followed by usually a space but also period or comma due to OCR noise
        (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ + #last name, first name; spaces are escaped due to re.VERBOSE
        (?P<age>[\d]+)(.0)?\ + #age; space escaped
        (?P<school>[A-Za-z \-'()\d.]+)\ + #school name
        (?P<seedTime>(\d+:)?\d{2}\.\d{2}|NT)\ + #seed time
        (?P<divsTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,})\ * #divs time
        (?P<qualified>q?) #qualified indicator, possibly with some OCR noise""",
        re.VERBOSE),

    "divsRelayTeam": re.compile(
        r'''(?P<rank>[\-\d]+)\ +
        (?P<school>[A-Za-z \-'()\d.]+)\ +
        (?P<designation>[A-F])\ +
        (?P<seedTime>(\d+:)?\d{2}\.\d{2}|NT)\ +
        (?P<divsTime>(\d+:)?\d{2}\.\d{2}|[A-Z]{2,})\ *
        (?P<qualified>q?)''',
        re.VERBOSE),

    "citiesInd": re.compile(
        r"""(?P<rank>[\-\d]+)(.0)?\ + #rank, followed by usually a space but also period or comma due to OCR noise
        (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ + #last name, first name; spaces are escaped due to re.VERBOSE
        (?P<age>[\d]+)(.0)?\ + #age; space escaped
        (?P<school>[A-Za-z \-'()\d.]+)\ + #school name
        (?P<divsTime>(\d+:)?\d{2}\.\d{2}|DQ|NS|NT)\ + #divs time
        x?(?P<citiesTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,}) #cities time""",
        re.VERBOSE),

    "citiesRelayTeam": re.compile(
        r"""(?P<rank>[\-\d]+)\ +
        (?P<school>[A-Za-z \-'()\d.]+)\ +
        (?P<designation>[A-F])\ +
        (?P<divsTime>(\d+:)?\d{2}\.\d{2}|DQ|NS|NT)\ +
        x?(?P<citiesTime>(\d+:)?\d{2}\.\d{2}|[A-Z]{2,})""",
        re.VERBOSE),

    "relayParticipant": re.compile(
        r"""(?P<relayPos>\d)\)\ +
        (?P<lastname>[A-Za-z \-']+),\ 
        (?P<firstname>[A-Za-z \-']+)\ +
        (M|W)?(?P<age>\d+)""",
        re.VERBOSE)
}

db = SqliteDatabase("2019.db", pragmas = {
    'foreign_keys': 1,
    'ignore_check_constraints': 0})

class School(Model):
    name = CharField()

    class Meta:
        database = db

    def __str__(self):
        return self.name

    def teamSize(self, year):
        results = (
            Result.select(Result.swimmer)
            .where((Result.school == self) & (Result.year == year))
            .tuples()
        )
        return len(set(results))

    virtFields = ["teamSize"]

class Swimmer(Model):
    firstName = CharField()
    lastName = CharField()
    gender = CharField()

    class Meta:
        database = db

    def __str__(self):
        return "{}, {}".format(self.lastName, self.firstName)

    def lifetimeNumRelays(self, year):
        relays = (
            RelayParticipant.select()
            .join(RelayResult)
            .where((RelayParticipant.swimmer == self) & (RelayResult.year <= year))
            .tuples()
        )
        return len(relays)

    def lifetimeNumEvents(self, year):
        results = (
            Result.select()
            .where((Result.swimmer == self) & (Result.year <= year))
            .tuples()
        )
        return len(results)

    def lifetimeStrokes(self):
        results = Result.select(Event.stroke).join(Event).where(Result.swimmer == self).dicts()
        strokeSet = {result["stroke"] for result in results}
        return strokeSet

    virtFields = ["lifetimeNumRelays", "lifetimeNumEvents"]

class Event(Model):
    age = IntegerField(null=True)
    distance = IntegerField()
    stroke = CharField()
    gender = CharField()
    isRelay = BooleanField()

    class Meta:
        database = db

    def __str__(self):
        return "{} {} {}m {} {}".format(
            self.gender, 
            self.age if self.age is not None else "Open",
            self.distance, 
            self.stroke,
            "Relay" if self.isRelay else "")

    def numSwimmers(self, year):
        return sum(1 for result in self.results if result.divsRank is not None and result.year == year)

    def numQualified(self, year):
        return sum(1 for result in self.results if result.qualified and result.year == year)

    virtFields = []

class Result(Model):
    divsRank = IntegerField(null=True)
    finalRank = IntegerField(null=True)
    swimmer = ForeignKeyField(Swimmer, backref = "results")
    swimmerage = IntegerField(null=True)
    school = ForeignKeyField(School, backref = "results")
    event = ForeignKeyField(Event, backref = "results")
    seedTime = FloatField(null=True)
    divsTime = FloatField(null=True)
    finalTime = FloatField(null=True)
    qualified = BooleanField()
    year = IntegerField()

    class Meta:
        database = db
    
    def __str__(self):
        return f"{self.divsRank}\t{self.swimmer} - {self.school}\t{self.divsTime}"

    
    def points(self):
        from tradPointOut import rankToPoints2017
        return rankToPoints2017(self.finalRank)

    
    def seedSpeed(self):
        try:
            return self.event.distance / self.seedTime
        except TypeError:
            return None

    
    def divsSpeed(self):
        try:
            return self.event.distance / self.divsTime
        except TypeError:
            return None

    def numRelays(self):
        relays = (
            RelayParticipant.select(RelayParticipant.swimmer)
            .join(RelayResult)
            .where((RelayParticipant.swimmer == self.swimmer) & (RelayResult.year == self.year))
            .tuples()
        )
        return len(relays)

    def numEvents(self):
        results = (
            Result.select(Result.swimmer)
            .where((Result.swimmer == self.swimmer) & (Result.year == self.year))
            .tuples()
        )
        return len(results)

    def strokes(self):
        results = (
            Result.select(Event.stroke).join(Event).
            where((Result.swimmer == self.swimmer) & (Result.year == self.year))
            .dicts()
        )
        strokeSet = {result["stroke"] for result in results}
        return strokeSet

    def swimmerName(self):
        return str(self.swimmer)

    
    virtFields = ["divsSpeed", "swimmerName"]


class RelayResult(Model):
    divsRank = IntegerField(null=True)
    finalRank = IntegerField(null=True)
    school = ForeignKeyField(School, backref = "relayresults")
    event = ForeignKeyField(Event, backref = "relayresults")
    designation = CharField(null=True)
    seedTime = FloatField(null=True)
    divsTime = FloatField(null=True)
    finalTime = FloatField(null=True)
    qualified = BooleanField()
    year = IntegerField()

    class Meta:
        database = db

    def __str__(self):
        return "{}->{} {} {} {}->{}".format(
            self.divsRank, self.finalRank, 
            self.school.name, self.designation,
            self.divsTime, self.finalTime)

    def points(self):
        from tradPointOut import rankToPoints2017
        return rankToPoints2017(self.finalRank)

    def divsSpeed(self):
        try:
            return self.event.distance / self.divsTime
        except TypeError:
            return None

    def numRelays(self):
        numRelaysList = []
        for swimmer in Swimmer.select().join(RelayParticipant).where(RelayParticipant.relay == self):
            query = (
                RelayParticipant.select(RelayParticipant.swimmer)
                .join(RelayResult)
                .where((RelayParticipant.swimmer == swimmer) & (RelayResult.year == self.year))
                .tuples()
                )
            numRelaysList.append(len(query))
        return np.mean(numRelaysList)

    def numEvents(self):
        numEventsList = []
        for swimmer in Swimmer.select().join(RelayParticipant).where(RelayParticipant.relay == self):
            query = (
                Result.select(Result.swimmer)
                .where((Result.swimmer == swimmer) & (Result.year == self.year))
                .tuples()
                )
            numEventsList.append(len(query))
        return np.mean(numEventsList)

    def swimmerName(self):
        return f"{self.school} - {self.designation}"

    virtFields = ["divsSpeed", "swimmerName"]


class RelayParticipant(Model):
    swimmer = ForeignKeyField(Swimmer, backref = "relays")
    relay = ForeignKeyField(RelayResult, backref = "swimmers")
    pos = IntegerField()
    age = IntegerField(null=True)

    class Meta:
        database = db

def strToTime(s: str) -> float:
    if ":" in s:
        t = s.split(":")
        return int(t[0]) * 60 + float(t[1])
    else:
        try:
            s = float(s)
            assert 0 < s < 60
            return s
        except (AssertionError, ValueError):
            print("StrToTime Warning: no time for value", s)
            return None

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

def getEventFromLine(line, matchDict):
    if "Swim-off" in line:
        return None
    isRelay = False if matchDict["relay"] is None else True
    dist = int(matchDict["distance"])
    if isRelay:
        if dist == 50:
            dist = 200
        elif dist == 100:
            dist = 400
    
    return Event.get_or_create(
        gender = matchDict["gender"],
        stroke = matchDict["stroke"],
        isRelay = False if matchDict["relay"] is None else True,
        age = ageMatch(int(matchDict["age"])) if matchDict["age"].isdecimal() else None,
        distance = dist
    )

def getDivsInd(matchDict, currentEvent):
    #print(matchDict)
    school = School.get_or_create(name = matchDict["school"].strip())
    swimmer = Swimmer.get_or_create(
        firstName = matchDict["firstName"].strip(),
        lastName = matchDict["lastName"].strip(),
        defaults = {
            "gender": currentEvent.gender
        }
    )
    result = Result.get_or_create(
        divsRank = int(matchDict["rank"]) if matchDict["rank"].isdecimal() else None,
        swimmer = swimmer[0],
        school = school[0],
        event = currentEvent,
        seedTime = strToTime(matchDict["seedTime"]),
        divsTime = strToTime(matchDict["divsTime"]),
        defaults = {
            "swimmerage": ageMatch(int(matchDict["age"])),
            "qualified": matchDict["qualified"] is not None and 'q' in matchDict["qualified"],
            "year": YEAR
        }
    )

def getDivsRelay(matchDict, currentEvent):
    #print(matchDict)
    school = School.get_or_create(name = matchDict["school"].strip())
    result = RelayResult.get_or_create(
        divsRank = int(matchDict["rank"]) if matchDict["rank"].isdecimal() else None,
        school = school[0],
        designation = matchDict["designation"],
        event = currentEvent,
        seedTime = strToTime(matchDict["seedTime"]),
        divsTime = strToTime(matchDict["divsTime"]),
        defaults = {
            "qualified": matchDict["qualified"] is not None and 'q' in matchDict["qualified"],
            "year": YEAR
        }
    )
    return result[0]

def updateRelayParticipant(matchDict, relay, event):
    swimmer = Swimmer.get_or_create(
        firstName = matchDict["firstname"].strip(),
        lastName = matchDict["lastname"].strip(),
        defaults = {
            "gender": event.gender
        }
    )[0]
    participant = RelayParticipant.get_or_create(
        swimmer = swimmer,
        relay = relay,
        pos = int(matchDict["relayPos"]),
        age = ageMatch(int(matchDict["age"])) if matchDict["age"].isdecimal() else None
    )

def updateCitiesInd(matchDict, currentEvent):
    #print(matchDict)
    try:
        swimmer = Swimmer.get(
            firstName = matchDict["firstName"].strip(),
            lastName = matchDict["lastName"].strip(),
            gender = currentEvent.gender
        )
        result = Result.get(
            swimmer = swimmer,
            event = currentEvent,
            divsTime = strToTime(matchDict["divsTime"]),
            year = YEAR
        )
    except Exception:
        traceback.print_exc()
        return
    result.finalRank = int(matchDict["rank"]) if matchDict["rank"].isdecimal() else None
    result.finalTime = strToTime(matchDict["citiesTime"])
    result.save()

def updateCitiesRelay(matchDict, currentEvent):
    schoolName = matchDict["school"].strip()
    schoolAliases = {
        "ME LaZerte High School-AB": "M.E. LaZerte High School-AB"
    }
    if schoolName in schoolAliases:
        schoolName = schoolAliases[schoolName]

    school = School.get(name = schoolName)
    try:
        result = RelayResult.get(
            school = school,
            event = currentEvent,
            divsTime = strToTime(matchDict["divsTime"]),
            year = YEAR
        )
        result.finalRank = int(matchDict["rank"]) if matchDict["rank"].isdecimal() else None
        result.finalTime = strToTime(matchDict["citiesTime"])
        result.save()
    except Exception:
        traceback.print_exc()
        return


def readPDFtoDB(pdfObj, filename):
    for pageNum in range(pdfObj.numPages):
        try:
            table = tabula.read_pdf(filename, pages=pageNum+1, guess=False)
        except Exception:
            traceback.print_exc()
            continue

        tableStr = table.to_string(
            index=False, 
            index_names=False, 
            na_rep='', 
            header=False
        )
        print(tableStr)
        tablerows = tableStr.split('\n')
        
        for line in tablerows:
            for linetype, regex in regexes.items():
                if regex.search(line):
                    matchDict = regex.search(line).groupdict()
                    if linetype == "event":
                        print(matchDict)
                        currentEvent = getEventFromLine(line, matchDict)[0]

                    elif currentEvent is not None and "divs" in filename:
                        if linetype == "divsInd":
                            print(matchDict)
                            getDivsInd(matchDict, currentEvent)
                        elif linetype == "divsRelayTeam":
                            print(matchDict)
                            currentRelay = getDivsRelay(matchDict, currentEvent)
                        elif linetype == "relayParticipant":
                            for match in regexes["relayParticipant"].finditer(line):
                                print(match.groupdict())
                                updateRelayParticipant(match.groupdict(), currentRelay, currentEvent)

                    elif currentEvent is not None and "cities" in filename:
                        if linetype == "citiesInd":
                            print(matchDict)
                            updateCitiesInd(matchDict, currentEvent)
                        elif linetype == "citiesRelayTeam":
                            print(matchDict)
                            updateCitiesRelay(matchDict, currentEvent)

            


if __name__ == "__main__":
    input("Confirm you want to rewrite DB!")
    YEAR = 2019
    filename = "data/{} cities.pdf".format(YEAR)
    pdfObj = PyPDF2.PdfFileReader(filename)

    pd.set_option('display.max_colwidth', -1)

    db.connect()
    db.create_tables([School, Swimmer, Result, Event, RelayResult, RelayParticipant])
    readPDFtoDB(pdfObj, filename)
    db.close()
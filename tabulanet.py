import pandas as pd
import tabula
import PyPDF2
import re
import traceback
from peewee import *

eventRegex = re.compile(
    r'''Event\ \d+\ +
    (?P<gender>Boys|Girls|Mixed)\ 
    (?P<age>\d{2}|Open).+
    (?P<distance>50|100|200|400).+Meter\ 
    (?P<stroke>[A-Za-z]+)
    (?P<relay>\ Relay)?''',
    re.VERBOSE)

divsRegex = re.compile(
    r"""(?P<rank>[\-\d]+)(.0)?\ + #rank, followed by usually a space but also period or comma due to OCR noise
    (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ + #last name, first name; spaces are escaped due to re.VERBOSE
    (?P<age>[\d]+)(.0)?\ + #age; space escaped
    (?P<school>[A-Za-z \-'()\d.]+)\ + #school name
    (?P<seedTime>(\d+:)?\d{2}\.\d{2}|NT)\ + #seed time
    (?P<divsTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,})\ * #divs time
    (?P<qualified>q?) #qualified indicator, possibly with some OCR noise""",
    re.VERBOSE)

citiesRegex = re.compile(
    r"""(?P<rank>[\-\d]+)(.0)?\ + #rank, followed by usually a space but also period or comma due to OCR noise
    (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ + #last name, first name; spaces are escaped due to re.VERBOSE
    (?P<age>[\d]+)(.0)?\ + #age; space escaped
    (?P<school>[A-Za-z \-'()\d.]+)\ + #school name
    (?P<divsTime>(\d+:)?\d{2}\.\d{2}|NT)\ + #seed time
    (?P<citiesTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,})\ * #divs time""",
    re.VERBOSE)

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

pd.set_option('display.max_colwidth', -1)
db.connect()
db.create_tables([School, Swimmer, Result, Event])

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
            #print(line.strip())
            matchDivs = divsRegex.search(line)
            matchEvent = eventRegex.search(line)
            matchCities = citiesRegex.search(line)
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
                    age = ageMatch(int(matchDict["age"])) if matchDict["age"].isdecimal() else None,
                    distance = matchDict["distance"]
                )
            elif matchDivs and currentEvent is not None and "divs" in filename:
                matchDict = matchDivs.groupdict()
                print(matchDict)
                school = School.get_or_create(name = matchDict["school"].strip())
                swimmer = Swimmer.get_or_create(
                    firstName = matchDict["firstName"].strip(),
                    lastName = matchDict["lastName"].strip(),
                    defaults = {
                        "gender": currentEvent[0].gender,
                        "school": school[0]
                    }
                )
                result = Result.get_or_create(
                    divsRank = int(matchDict["rank"]) if matchDict["rank"].isdecimal() else None,
                    swimmer = swimmer[0],
                    event = currentEvent[0],
                    seedTime = strToTime(matchDict["seedTime"]),
                    divsTime = strToTime(matchDict["divsTime"]),
                    defaults = {
                        "swimmerage": ageMatch(int(matchDict["age"])),
                        "qualified": matchDict["qualified"] is not None and 'q' in matchDict["qualified"],
                        "year": YEAR
                    }
                )
            elif matchCities and currentEvent is not None and "cities" in filename:
                matchDict = matchCities.groupdict()
                print(matchDict)
                swimmer = Swimmer.get(
                    firstName = matchDict["firstName"].strip(),
                    lastName = matchDict["lastName"].strip()
                )
                result = Result.get(
                    swimmer = swimmer,
                    event = currentEvent[0],
                    divsTime = strToTime(matchDict["divsTime"]),
                    year = YEAR
                )
                result.finalRank = int(matchDict["rank"]) if matchDict["rank"].isdecimal() else None
                result.finalTime = strToTime(matchDict["citiesTime"])
                result.save()

if __name__ == "__main__":
    YEAR = 2018
    filename = "data/{} cities.pdf".format(YEAR)
    pdfObj = PyPDF2.PdfFileReader(filename)

    pd.set_option('display.max_colwidth', -1)

    db.connect()
    #db.create_tables([School, Swimmer, Result, Event])
    readPDFtoDB(pdfObj, filename)
    db.close()
import tabula
import PyPDF2
import re
import traceback
from peewee import *

YEAR = 2018

filename = "data/{} divs.pdf".format(YEAR)
pdfObj = PyPDF2.PdfFileReader(filename)


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


db.connect()
db.create_tables([School, Swimmer, Result, Event])

for pageNum in range(pdfObj.numPages):
    pageObj = pdfObj.getPage(pageNum)
    pageTxt = pageObj.extractText()
    eventMatch = eventRegex.search(pageTxt)
    if eventMatch:
        matchDict = eventMatch.groupdict()
        print(matchDict)
        currentEvent = Event.get_or_create(
            gender = matchDict["gender"],
            stroke = matchDict["stroke"],
            isRelay = False if matchDict["relay"] is None else True,
            age = ageMatch(int(matchDict["age"])) if matchDict["age"].isdecimal() else None,
            distance = int(matchDict["distance"])
        )
    try:
        table = tabula.read_pdf(filename, pages=pageNum+1, multiple_tables=True).to_string(index=False, index_names=False, na_rep='')
        print(len(table))
    except Exception:
        traceback.print_exc()
        continue
    
    print(table)
    for match in divsRegex.finditer(table):
        matchDict = match.groupdict()
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

db.close()
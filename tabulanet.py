import tabula
import PyPDF2
import re

YEAR = 2016

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
    r"""(?P<rank>[\-\d]+)\ + #rank, followed by usually a space but also period or comma due to OCR noise
    (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ + #last name, first name; spaces are escaped due to re.VERBOSE
    (?P<age>[\d]+)(.0)?\ + #age; space escaped
    (?P<school>[A-Za-z \-'()\d.]+)\ + #school name
    (?P<seedTime>(\d+:)?\d{2}\.\d{2}|NT)\ + #seed time
    (?P<divsTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,})\ + #divs time
    (?P<qualified>q?) #qualified indicator, possibly with some OCR noise""",
    re.VERBOSE)

citiesRegex = re.compile(
    r"""(?P<rank>[\-\d]+)\ + #rank, followed by usually a space but also period or comma due to OCR noise
    (?P<lastName>[A-Za-z \-']+),\ (?P<firstName>[A-Za-z \-']+)\ + #last name, first name; spaces are escaped due to re.VERBOSE
    (?P<age>[\d]+)(.0)?\ + #age; space escaped
    (?P<school>[A-Za-z \-'()\d.]+)\ + #school name
    (?P<divsTime>(\d+:)?\d{2}\.\d{2}|NT)\ + #seed time
    (?P<citiesTime>(\d+:)?\d{2}\.?\d{2}|[A-Z]{2,})\ + #divs time""",
    re.VERBOSE)


for pageNum in range(pdfObj.numPages):
    pageObj = pdfObj.getPage(pageNum)
    pageTxt = pageObj.extractText()
    eventMatch = eventRegex.search(pageTxt)
    if eventMatch:
        print(eventMatch.groupdict())
    table = tabula.read_pdf(filename, pages=pageNum+1).to_string(index=False, index_names=False)
    print(table)
    for match in divsRegex.finditer(table):
        print(match.groupdict())
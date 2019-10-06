import tabula
import PyPDF2
import re

eventRegex = re.compile(
    r'''Event\ \d+\ +
    (?P<gender>Boys|Girls|Mixed)\ 
    (?P<age>\d{2}|Open).+
    (?P<distance>50|100|200|400).+Meter\ 
    (?P<stroke>[A-Za-z]+)
    (?P<relay>\ Relay)?''',
    re.VERBOSE)

filename = "data/2016 divs.pdf"
pdfObj = PyPDF2.PdfFileReader(filename)

for pageNum in range(pdfObj.numPages):
    pageObj = pdfObj.getPage(pageNum)
    pageTxt = pageObj.extractText()
    eventMatch = eventRegex.search(pageTxt)
    if eventMatch:
        print(eventMatch.groupdict())
    df = tabula.read_pdf(filename, pages=pageNum+1)
    print(df)
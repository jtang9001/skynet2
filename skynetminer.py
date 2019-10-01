from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBox

document = open('data/2015 divs.pdf', 'rb')

#Create resource manager
rsrcmgr = PDFResourceManager()

# Set parameters for analysis.
laparams = LAParams(char_margin=5.0, line_margin=0.01, word_margin=0.1, line_overlap=0.99, boxes_flow=-1.0)

# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)

for page in PDFPage.get_pages(document):
    interpreter.process_page(page)

    # receive the LTPage object for the page.
    layout = device.get_result()
    for element in layout:
        if isinstance(element, LTTextBox):
            print(element.get_text())

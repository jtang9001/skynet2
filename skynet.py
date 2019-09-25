import pdf2image as pdf

def getPDFPages(pdfPath):
    return pdf.convert_from_path(pdfPath)

print(getPDFPages("data/2017 divs.pdf"))

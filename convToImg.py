import pdf2image as pdf
import os
import glob

def getPDFPages(pdfPath):
    outputFolder = pdfPath[:-4]
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        return pdf.convert_from_path(pdfPath, output_folder=outputFolder, fmt="png")
    else:
        return

for path in glob.glob("data/*divs girls.pdf"):
    print(path)
    pages = getPDFPages(path)
import pdf2image as pdf
import os
import glob

def getPDFPages(pdfPath):
    outputFolder = pdfPath[:-4]
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        return pdf.convert_from_path(
            pdfPath, 
            dpi=400, 
            output_folder=outputFolder, 
            fmt="png",
            thread_count=4
        )
    else:
        return

for path in glob.glob("data/*cities.pdf"):
    print(path)
    pages = getPDFPages(path)
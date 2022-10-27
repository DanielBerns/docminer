# extract_doc_info.py

from PyPDF2 import PdfFileReader
import sys

def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
        # get the first page
        page = pdf.getPage(1)
        print(page)
        print('Page type: {}'.format(str(type(page))))
        text = page.extractText()
        print(text)

    report = f"""
    Information about {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """

    print(report)
    return information

def text_extractor(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)

if __name__ == '__main__':
    path = sys.argv[1]
    extract_information(path)


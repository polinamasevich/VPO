from pdf2image import convert_from_path
from pypdf import PdfReader
pdf=r'D:\igi_lab5\output\pdf\Подготовка к защите лабораторной.pdf'
r=PdfReader(pdf); print('pages',len(r.pages))
imgs=convert_from_path(pdf,dpi=100,poppler_path=r'C:\Users\polix\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin')
for i,im in enumerate(imgs,1): im.save(fr'D:\igi_lab5\tmp\pdfs\checked-final-{i:02}.png')

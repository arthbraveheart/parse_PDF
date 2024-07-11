# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:43:06 2024

@author: ArthurRodrigues
"""
from pypdf import PdfReader
import re
import time
#t1 = time.time()
reader = PdfReader("C:/Users/ArthurRodrigues/Codes/Pricing/pricing_pckg/report/export/249 Ponto 12-2012 a 11-2017.pdf")

#page1 = reader.pages[0].extract_text()

#pattern = re.compile(r"\n(.*?)")

#lynes = page1.split('\n')#re.findall(pattern,page1)
def dias_trabalhados(lines : list ) -> int:
    it_lines = iter(lines)
    
    count = 0
    
    while True:
            if 'Matricula' not in next(it_lines):
                continue
            else:    
                line = next(it_lines)
                while 'Historico' not in line:
                    count+=1 if line.count(':')>0 else 0
                    line = next(it_lines)
                break
    period = re.findall(r"(\w+)\s+\/\s+(\d+)", lines[3])[0]        
    print((period,count))        
    return count

def all_days(pdf):
    COUNT = []
    for page in pdf.pages:
        pg = page.extract_text()
        lynes = pg.split('\n')
        COUNT.append(dias_trabalhados(lynes))
    return COUNT

t1 = time.time()
alll = all_days(reader)
print(time.time() - t1)

    
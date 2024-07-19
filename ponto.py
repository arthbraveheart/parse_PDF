# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:43:06 2024

@author: ArthurRodrigues
"""
from pypdf import PdfReader
import os
import re
import time
import pandas as pd
import json
#t1 = time.time()
#reader = PdfReader("C:/Users/ArthurRodrigues/Codes/Pricing/pricing_pckg/report/export/249 Ponto 12-2012 a 11-2017.pdf")

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
    #name   = re.findall(r"Empregado\s+:\s+(\w+.*)\s+Categoria", lines[8])[0].strip()       
    print((period,count))        
    return (period,count)

def all_days(pdf):
    COUNT = []
    name   = re.findall(r"Empregado\s+:\s+(\w+.*)\s+Categoria", pdf.pages[0].extract_text())[0].strip()
    matricula = re.findall(r"Matricula\s+:\s+(\d+.*)\s+", pdf.pages[0].extract_text())[0].strip()
    for page in pdf.pages:
        pg = page.extract_text()
        lynes = pg.split('\n')
        COUNT.append(dias_trabalhados(lynes))
    return matricula,name,COUNT


pontos_path = 'C:/Users/ArthurRodrigues/Codes/Work/Documentos Perito - final'
lstdir      = os.listdir(pontos_path)
lstdir.pop(151)
lstdir.pop(151)
lstdir.pop(151)
lstdir.pop(135)
lstdir.pop(2)
lstdir.pop(140)
lstdir.pop(133)
t1 = time.time()
all_pontos = []
for matricula in lstdir:
    pontos = pontos_path + '/' + matricula + '/' + 'Ponto'
    pdfs = []
    for ponto in os.listdir(pontos):
        if '.pdf' in ponto:
            pdfs.append(ponto)
        else:
            continue 
    for pdf in pdfs:
        path = pontos + '/' + pdf
        all_pontos.append(path)
        
pontos = []

for ponto in all_pontos:
    reader = PdfReader(ponto)
    alll = all_days(reader)
    pontos.append(alll)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(pontos, f)
    
see = pd.read_json('C:/Users/ArthurRodrigues/Codes/Work/data.json')
shape = see.shape[0]

for i in range(shape):
    
    first = pd.DataFrame(see.iloc[i,2], columns=['Data','Dias Trabalhados'])
    title = str(see.iloc[i,0]) + str(see.iloc[i,1])
    title = str(see.iloc[i,0]) + ' - '+str(see.iloc[i,1])
    
    first.to_excel(f'C:/Users/ArthurRodrigues/Codes/Work/Compilado/{title}({i}).xlsx')


#alll = all_days(reader)
print(time.time() - t1)

    
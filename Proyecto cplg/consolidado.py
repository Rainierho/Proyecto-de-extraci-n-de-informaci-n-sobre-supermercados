import pandas as pd
from centralmadeirense import centralmadeirense_scrappy
from plazas import plazas_scrappy
from licores_mundiales import licores_mundiales_scrappy
from gama import gama_scraping
import datetime
dia = datetime.datetime.now()
dia_actual = f'{dia.day}-{dia.month}-{dia.year}'

g=gama_scraping()

l=licores_mundiales_scrappy()

c =centralmadeirense_scrappy()

p= plazas_scrappy()

consolidado = pd.concat([c,p,l,g])
consolidado.to_excel(f'consolidado_{dia_actual}.xlsx')
    





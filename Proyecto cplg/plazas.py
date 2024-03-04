import requests   #hacer solicitudes a paginas web
from bs4 import BeautifulSoup #procesamiento de texto html
import pandas as pd #Dataframes
import urllib3  #hacer solicitudes a paginas web
import time
import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #deshabilita advertencias de seguridad al conectarse con paginas web.

def plazas_scrappy():
    dia = datetime.datetime.now()
    dia_actual = f'{dia.day}/{dia.month}/{dia.year}'
    categories= ['frutas-y-vegetales','frutas-y-vegetales','refrigerados-y-congelados','viveres','cuidado-personal-y-salud','limpieza','licores','mascotas','hogar-y-temporada','otros']
    plazas ={}
    for i in range(50):
        for j in range(len(categories)):
            url=f'https://vallearriba.elplazas.com/{categories[j]}.html?p={i}'
            info = requests.get(url,verify=False)
            soup = BeautifulSoup(info.text,'html.parser')
            main = soup.find('div',class_='column main')
            product_layer = main.find('div',id='layer-product-list')
            list_of_product_div= product_layer.find('div',class_='products wrapper grid products-grid')
            time.sleep(1.5)
            if list_of_product_div:
                list_of_product= list_of_product_div.find('ol',class_='products list items product-items').find_all('li') #de aqui sale los items
                for k in list_of_product:
                    price =k.find('div',class_='product-item-info').find('div',class_='product details product-item-details').find('span',class_='price').get_text().strip()
                    name = k.find('div',class_='product-item-info').find('div',class_='product details product-item-details').find('strong',class_='product name product-item-name').get_text().strip()
                    plazas[name]={'PRECIO':price,
                                    'CATEGORIA':categories[j],
                                    'SUPERMERCADO' :'PLAZAS',
                                    'FECHA' : dia_actual,

                                }

    preciosp =[plazas[i]["PRECIO"] for i in plazas]
    categoriap =[plazas[i]["CATEGORIA"] for i in plazas]
    superp =[plazas[i]["SUPERMERCADO"] for i in plazas]
    fechap =[plazas[i]["FECHA"] for i in plazas]

    global plazas_data
    plazas_data=pd.DataFrame()
    plazas_data['producto']=plazas.keys()
    plazas_data["precio $"] = preciosp
    plazas_data["categoria"]=categoriap
    plazas_data['fecha']= fechap
    plazas_data["supermercado"]=superp
    plazas_data["precio $"]=plazas_data["precio $"].str.replace("$","", regex=False).str.strip()
    plazas_data["precio $"]=plazas_data["precio $"].str.replace(",",".", regex=False).str.strip()

    return plazas_data
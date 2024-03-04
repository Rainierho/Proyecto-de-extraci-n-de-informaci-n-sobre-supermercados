import requests   #hacer solicitudes a paginas web
from bs4 import BeautifulSoup #procesamiento de texto html
import pandas as pd #Dataframes
import urllib3  #hacer solicitudes a paginas web
import time
import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #deshabilita advertencias de seguridad al conectarse con paginas web.

def centralmadeirense_scrappy():
    dia = datetime.datetime.now()
    dia_actual = f'{dia.day}/{dia.month}/{dia.year}'
    lista_de_categorias =['viveres','refrigerados','fruteria-y-vegetales','cuidado-personal','articulos-de-limpieza','licores','hogar-temporada']
    centralmadeirense ={}
    for c in range(len(lista_de_categorias)):
        for i in range(1,30):
            url = f"https://tucentralonline.com/altos-mirandinos-23/comprar/{lista_de_categorias[c]}/page/{i}/?count=40"
            info= requests.get(url)
            soup = BeautifulSoup(info.text,"html.parser")
            product = soup.find('div',class_='archive-products')
            if product is not None:
              ul = product.find('ul',class_='products products-container list pcols-lg-4 pcols-md-3 pcols-xs-3 pcols-ls-2 pwidth-lg-4 pwidth-md-3 pwidth-xs-2 pwidth-ls-1')
              if ul is not None:
                products = ul.find_all('li')
                nombres_de_productos =[i.find('div',class_='product-content').find('a',class_='product-loop-title').find('h3',class_='woocommerce-loop-product__title').get_text() for i in products]
                precios = [i.find('div',class_='product-content').find('span',class_='price').find('span',class_='woocommerce-Price-amount amount').get_text().replace('#\xa0','') for i in products]
                time.sleep(2)
                for i,j in zip(nombres_de_productos,precios):
                    centralmadeirense[i] = {"PRECIO":j,
                                                        "CATEGORIA":lista_de_categorias[c],
                                                        "SUPERMERCADO":"CENTRALMADEIRENSE",
                                                        "FECHA": dia_actual,

                    }

    precioscm =[centralmadeirense[i]["PRECIO"] for i in centralmadeirense]
    categoriacm =[centralmadeirense[i]["CATEGORIA"] for i in centralmadeirense]
    supercm =[centralmadeirense[i]["SUPERMERCADO"] for i in centralmadeirense]
    fechacm =[centralmadeirense[i]["FECHA"] for i in centralmadeirense]

    global centralmadeirense_data
    centralmadeirense_data=pd.DataFrame()
    centralmadeirense_data['producto']=centralmadeirense.keys()
    centralmadeirense_data["precio $"] = precioscm
    centralmadeirense_data["categoria"]=categoriacm
    centralmadeirense_data ['fecha']= fechacm
    centralmadeirense_data["supermercado"]=supercm
    centralmadeirense_data["precio $"]=centralmadeirense_data["precio $"].str.replace("#","").str.strip()
    centralmadeirense_data["precio $"]=centralmadeirense_data["precio $"].str.replace(",",".").str.strip()
    
    return centralmadeirense_data
